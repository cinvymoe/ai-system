# Data Collector Module - API Documentation

## Overview

The Data Collector Module provides a comprehensive set of interfaces for building data collection, processing, and storage pipelines. The module follows a three-layer architecture:

1. **Data Collection Layer** - Interfaces for collecting data from various sources
2. **Data Processing Layer** - Interfaces for transforming and enriching data
3. **Data Storage Layer** - Interfaces for persisting data to storage backends

Additionally, the module provides cross-cutting interfaces for error handling, event management, and task tracking.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Data Collection Layer](#data-collection-layer)
- [Data Processing Layer](#data-processing-layer)
- [Data Storage Layer](#data-storage-layer)
- [Cross-Cutting Interfaces](#cross-cutting-interfaces)
- [Factory Interfaces](#factory-interfaces)
- [Data Models](#data-models)
- [Enumerations](#enumerations)
- [Error Handling](#error-handling)
- [Best Practices](#best-practices)

---

## Installation

The Data Collector Module is part of the backend package. No additional installation is required if you have the backend installed.

```python
from collectors.interfaces import (
    IDataSource,
    IProcessor,
    IStorageBackend,
    IErrorHandler,
    IEventEmitter,
)
```

---

## Quick Start

Here's a minimal example of using the data collector interfaces:

```python
import asyncio
from collectors.mocks import MockDataSource, MockProcessor, MockStorageBackend

async def quick_start():
    # Create components
    source = MockDataSource(source_id="sensor_001", data=b"temperature:25.5")
    processor = MockProcessor(name="normalizer")
    storage = MockStorageBackend(backend_id="main_db")
    
    # Collect data
    await source.connect()
    data = await source.collect()
    
    # Process data
    result = await processor.process({"raw": data.raw_data.decode()})
    
    # Store data
    await storage.connect()
    location = await storage.store(result.processed_data)
    
    print(f"Data stored at: {location.path}")
    
    # Cleanup
    await source.disconnect()
    await storage.disconnect()

asyncio.run(quick_start())
```

---

## Data Collection Layer

### IDataSource

Abstract interface for data sources. All concrete data sources must implement this interface.

#### Methods

##### `async connect() -> None`

Establishes connection to the data source.

**Raises:**
- `ConnectionError`: When connection fails

**Example:**
```python
source = CustomDataSource(source_id="sensor_001")
await source.connect()
```

##### `async disconnect() -> None`

Disconnects from the data source.

**Raises:**
- `ConnectionError`: When disconnection fails

##### `async collect() -> CollectedData`

Collects a single data sample from the source.

**Returns:**
- `CollectedData`: The collected data with metadata

**Raises:**
- `ConnectionError`: When data source is not connected
- `ValueError`: When collected data is invalid

**Example:**
```python
data = await source.collect()
print(f"Collected: {data.raw_data}")
```

##### `async collect_stream() -> AsyncIterator[CollectedData]`

Collects streaming data from the source.

**Yields:**
- `CollectedData`: Continuous stream of collected data

**Example:**
```python
async for data in source.collect_stream():
    print(f"Stream data: {data.raw_data}")
```

##### `get_source_id() -> str`

Returns the unique identifier for this data source.

**Returns:**
- `str`: Data source identifier

---

### IMetadataParser

Interface for parsing and validating metadata from collected data.

#### Methods

##### `async parse(collected_data: CollectedData) -> ParsedMetadata`

Parses metadata from collected data.

**Args:**
- `collected_data`: The raw collected data

**Returns:**
- `ParsedMetadata`: Parsed and structured metadata

**Raises:**
- `ValueError`: When data format is invalid

##### `async validate(metadata: ParsedMetadata) -> bool`

Validates metadata completeness and correctness.

**Args:**
- `metadata`: Parsed metadata to validate

**Returns:**
- `bool`: True if metadata is valid

---

### ICollectionManager

Interface for managing data sources and collection tasks.

#### Methods

##### `async register_source(source: IDataSource, config: Dict[str, Any]) -> str`

Registers a data source with the manager.

**Args:**
- `source`: Data source instance
- `config`: Configuration dictionary

**Returns:**
- `str`: Registered source ID

**Raises:**
- `ValueError`: When configuration is invalid

##### `async start_collection(source_id: str) -> str`

Starts a collection task for the specified source.

**Args:**
- `source_id`: Data source identifier

**Returns:**
- `str`: Task ID for tracking

**Raises:**
- `KeyError`: When source ID doesn't exist
- `RuntimeError`: When task is already running

##### `async get_statistics(source_id: str) -> CollectionStatistics`

Retrieves collection statistics for a source.

**Args:**
- `source_id`: Data source identifier

**Returns:**
- `CollectionStatistics`: Statistics including success/failure counts and timing

---

## Data Processing Layer

### IProcessor

Abstract interface for data processors. Each processor represents a single processing step.

#### Methods

##### `async process(data: Any) -> ProcessingResult`

Processes input data and returns the result.

**Args:**
- `data`: Input data to process

**Returns:**
- `ProcessingResult`: Result containing processed data or error information

**Raises:**
- `ValueError`: When input data is invalid

**Example:**
```python
processor = CustomProcessor(name="validator")
result = await processor.process(input_data)
if result.success:
    print(f"Processed: {result.processed_data}")
else:
    print(f"Error: {result.error}")
```

##### `get_processor_name() -> str`

Returns the unique name of this processor.

**Returns:**
- `str`: Processor name

##### `validate_input(data: Any) -> bool`

Validates input data before processing.

**Args:**
- `data`: Data to validate

**Returns:**
- `bool`: True if input is valid

---

### IPipeline

Interface for processing pipelines that execute multiple processors in sequence.

#### Methods

##### `async add_step(processor: IProcessor, order: int) -> str`

Adds a processing step to the pipeline.

**Args:**
- `processor`: Processor instance
- `order`: Execution order (lower numbers execute first)

**Returns:**
- `str`: Step ID

**Raises:**
- `ValueError`: When processor is invalid or order conflicts

##### `async execute(input_data: Any) -> PipelineResult`

Executes the entire pipeline.

**Args:**
- `input_data`: Initial input data

**Returns:**
- `PipelineResult`: Complete pipeline execution result

**Example:**
```python
pipeline = CustomPipeline()
await pipeline.add_step(validator, order=1)
await pipeline.add_step(transformer, order=2)
await pipeline.add_step(enricher, order=3)

result = await pipeline.execute(input_data)
if result.success:
    print(f"Final data: {result.final_data}")
```

##### `get_steps() -> list[PipelineStep]`

Returns all pipeline steps in execution order.

**Returns:**
- `list[PipelineStep]`: Ordered list of pipeline steps

---

### IProcessingManager

Interface for managing processors and pipelines.

#### Methods

##### `async register_processor(processor: IProcessor) -> str`

Registers a processor with the manager.

**Args:**
- `processor`: Processor instance

**Returns:**
- `str`: Processor ID

##### `async create_pipeline(pipeline_id: str) -> IPipeline`

Creates a new processing pipeline.

**Args:**
- `pipeline_id`: Unique pipeline identifier

**Returns:**
- `IPipeline`: New pipeline instance

##### `async get_statistics(pipeline_id: str) -> list[ProcessingStatistics]`

Retrieves processing statistics for a pipeline.

**Args:**
- `pipeline_id`: Pipeline identifier

**Returns:**
- `list[ProcessingStatistics]`: Statistics for each pipeline step

---

## Data Storage Layer

### IStorageBackend

Abstract interface for storage backends. All concrete storage implementations must implement this interface.

#### Methods

##### `async connect() -> None`

Connects to the storage backend.

**Raises:**
- `ConnectionError`: When connection fails
- `ValueError`: When configuration is invalid

##### `async store(data: Any) -> StorageLocation`

Stores data to the backend.

**Args:**
- `data`: Data to store

**Returns:**
- `StorageLocation`: Location information for the stored data

**Raises:**
- `ConnectionError`: When backend is not connected
- `ValueError`: When data format is invalid
- `RuntimeError`: When storage operation fails

**Example:**
```python
backend = CustomStorageBackend(backend_id="db_001")
await backend.connect()
location = await backend.store({"sensor": "temp_01", "value": 25.5})
print(f"Stored at: {location.path}")
```

##### `async query(criteria: QueryCriteria) -> List[Any]`

Queries data from the backend.

**Args:**
- `criteria`: Query criteria including filters, sorting, limit, and offset

**Returns:**
- `List[Any]`: List of matching data items

**Example:**
```python
criteria = QueryCriteria(
    filters={"sensor": "temp_01"},
    sort_by="timestamp",
    limit=10,
    offset=0
)
results = await backend.query(criteria)
```

##### `async delete(location_id: str) -> None`

Deletes data from the backend.

**Args:**
- `location_id`: Storage location identifier

**Raises:**
- `KeyError`: When location_id doesn't exist

---

### IStorageManager

Interface for managing storage backends and coordinating storage operations.

#### Methods

##### `async register_backend(backend: IStorageBackend, config: Dict[str, Any]) -> str`

Registers a storage backend with the manager.

**Args:**
- `backend`: Storage backend instance
- `config`: Backend configuration

**Returns:**
- `str`: Backend ID

##### `async store_data(backend_id: str, data: Any) -> StorageLocation`

Stores data to a specific backend.

**Args:**
- `backend_id`: Target backend identifier
- `data`: Data to store

**Returns:**
- `StorageLocation`: Storage location information

##### `async get_statistics(backend_id: str) -> StorageStatistics`

Retrieves storage statistics for a backend.

**Args:**
- `backend_id`: Backend identifier

**Returns:**
- `StorageStatistics`: Statistics including stored count and storage usage

---

## Cross-Cutting Interfaces

### IErrorHandler

Interface for handling system errors.

#### Methods

##### `async handle_error(error: ErrorInfo) -> None`

Handles an error.

**Args:**
- `error`: Error information

**Raises:**
- `RuntimeError`: When error handling fails

**Example:**
```python
handler = CustomErrorHandler()
error = ErrorInfo(
    error_type=ErrorType.VALIDATION,
    timestamp=datetime.now(),
    layer_name="processing",
    operation="validate",
    message="Invalid data format",
    details={"expected": "dict"},
    is_critical=False
)
await handler.handle_error(error)
```

##### `can_handle(error_type: ErrorType) -> bool`

Checks if this handler can handle a specific error type.

**Args:**
- `error_type`: Error type to check

**Returns:**
- `bool`: True if handler can handle this error type

---

### IEventEmitter

Interface for event-driven architecture support.

#### Methods

##### `async emit(event: SystemEvent) -> None`

Emits an event to all subscribers.

**Args:**
- `event`: System event to emit

**Example:**
```python
emitter = CustomEventEmitter()
event = SystemEvent(
    event_type=EventType.COLLECTION_COMPLETE,
    timestamp=datetime.now(),
    source="collection_manager",
    data={"items_collected": 100}
)
await emitter.emit(event)
```

##### `async subscribe(event_type: EventType, handler: Callable) -> str`

Subscribes to an event type.

**Args:**
- `event_type`: Type of event to subscribe to
- `handler`: Callback function to handle events

**Returns:**
- `str`: Subscription ID for later unsubscription

**Example:**
```python
async def on_collection_complete(event: SystemEvent):
    print(f"Collection completed: {event.data}")

sub_id = await emitter.subscribe(
    EventType.COLLECTION_COMPLETE,
    on_collection_complete
)
```

##### `async unsubscribe(subscription_id: str) -> None`

Unsubscribes from events.

**Args:**
- `subscription_id`: Subscription ID from subscribe()

---

### ITaskTracker

Interface for tracking asynchronous operations.

#### Methods

##### `async create_task(task_type: str) -> str`

Creates a new task for tracking.

**Args:**
- `task_type`: Type of task (e.g., "collection", "processing")

**Returns:**
- `str`: Task ID

##### `async update_status(task_id: str, status: TaskStatus) -> None`

Updates task status.

**Args:**
- `task_id`: Task identifier
- `status`: New task status

##### `async update_progress(task_id: str, progress: float) -> None`

Updates task progress.

**Args:**
- `task_id`: Task identifier
- `progress`: Progress value (0.0 to 1.0)

##### `async get_task_info(task_id: str) -> TaskInfo`

Retrieves complete task information.

**Args:**
- `task_id`: Task identifier

**Returns:**
- `TaskInfo`: Complete task information

---

## Factory Interfaces

### ICollectionLayerFactory

Factory for creating collection layer components.

#### Methods

##### `create_collection_manager() -> ICollectionManager`

Creates a collection manager instance.

##### `create_metadata_parser() -> IMetadataParser`

Creates a metadata parser instance.

---

### IProcessingLayerFactory

Factory for creating processing layer components.

#### Methods

##### `create_processing_manager() -> IProcessingManager`

Creates a processing manager instance.

##### `create_pipeline() -> IPipeline`

Creates a pipeline instance.

---

### IStorageLayerFactory

Factory for creating storage layer components.

#### Methods

##### `create_storage_manager() -> IStorageManager`

Creates a storage manager instance.

---

## Data Models

### CollectedData

Represents collected raw data with metadata.

**Fields:**
- `source_id: str` - Data source identifier
- `timestamp: datetime` - Collection timestamp
- `data_format: str` - Format of the raw data
- `collection_method: str` - Method used for collection
- `raw_data: bytes` - Raw binary data
- `metadata: Dict[str, Any]` - Additional metadata

---

### ParsedMetadata

Represents parsed and validated metadata.

**Fields:**
- `schema: Dict[str, Any]` - Metadata schema
- `quality_indicators: Dict[str, float]` - Data quality metrics
- `source_attributes: Dict[str, Any]` - Source-specific attributes
- `is_valid: bool` - Validation status
- `validation_errors: list[str]` - List of validation errors

---

### ProcessingResult

Represents the result of a processing operation.

**Fields:**
- `success: bool` - Whether processing succeeded
- `processed_data: Optional[Any]` - Processed data (if successful)
- `error: Optional[str]` - Error message (if failed)
- `processing_time: float` - Time taken to process

---

### StorageLocation

Represents the location of stored data.

**Fields:**
- `backend_id: str` - Storage backend identifier
- `location_id: str` - Unique location identifier
- `path: str` - Storage path
- `created_at: datetime` - Storage timestamp

---

### ErrorInfo

Represents error information.

**Fields:**
- `error_type: ErrorType` - Type of error
- `timestamp: datetime` - When error occurred
- `layer_name: str` - Layer where error occurred
- `operation: str` - Operation that failed
- `message: str` - Error message
- `details: Dict[str, Any]` - Additional error details
- `is_critical: bool` - Whether error is critical

---

## Enumerations

### CollectionStatus

Collection task status values:
- `IDLE` - Task is idle
- `RUNNING` - Task is running
- `PAUSED` - Task is paused
- `STOPPED` - Task is stopped
- `ERROR` - Task encountered an error

### TaskStatus

Async task status values:
- `PENDING` - Task is pending
- `RUNNING` - Task is running
- `COMPLETED` - Task completed successfully
- `FAILED` - Task failed
- `CANCELLED` - Task was cancelled

### EventType

System event types:
- `COLLECTION_START` - Collection started
- `COLLECTION_COMPLETE` - Collection completed
- `PROCESSING_START` - Processing started
- `PROCESSING_COMPLETE` - Processing completed
- `STORAGE_START` - Storage started
- `STORAGE_COMPLETE` - Storage completed
- `ERROR_OCCURRED` - Error occurred

### ErrorType

Error categories:
- `CONFIGURATION` - Configuration error
- `CONNECTION` - Connection error
- `VALIDATION` - Validation error
- `PROCESSING` - Processing error
- `STORAGE` - Storage error

---

## Error Handling

The module uses structured error handling through the `ErrorInfo` model and `IErrorHandler` interface.

### Error Flow

1. Error occurs in any layer
2. Error is wrapped in `ErrorInfo` with context
3. Error is passed to registered error handlers
4. Error event is emitted for monitoring
5. Error is returned or propagated as appropriate

### Example

```python
try:
    result = await processor.process(data)
except Exception as e:
    error = ErrorInfo(
        error_type=ErrorType.PROCESSING,
        timestamp=datetime.now(),
        layer_name="processing",
        operation="process",
        message=str(e),
        details={"exception": type(e).__name__},
        is_critical=True
    )
    await error_handler.handle_error(error)
    await event_emitter.emit(SystemEvent(
        event_type=EventType.ERROR_OCCURRED,
        timestamp=datetime.now(),
        source="processor",
        data={"error": error.message}
    ))
```

---

## Best Practices

### 1. Always Use Async/Await

All I/O operations are asynchronous. Always use `async`/`await`:

```python
# Good
await source.connect()
data = await source.collect()

# Bad
source.connect()  # This won't work!
```

### 2. Handle Errors Gracefully

Always handle potential errors:

```python
try:
    await source.connect()
    data = await source.collect()
except ConnectionError as e:
    await error_handler.handle_error(create_error_info(e))
finally:
    await source.disconnect()
```

### 3. Clean Up Resources

Always disconnect from sources and backends:

```python
source = MockDataSource(source_id="sensor_001")
try:
    await source.connect()
    # ... use source ...
finally:
    await source.disconnect()
```

### 4. Use Events for Monitoring

Emit events for significant operations:

```python
await emitter.emit(SystemEvent(
    event_type=EventType.COLLECTION_START,
    timestamp=datetime.now(),
    source="my_collector",
    data={"source_id": source_id}
))
```

### 5. Validate Configurations

Always validate configurations before use:

```python
async def register_source(self, source: IDataSource, config: Dict[str, Any]) -> str:
    # Validate config
    if not self._validate_config(config):
        raise ValueError("Invalid configuration")
    
    # Register source
    source_id = source.get_source_id()
    self._sources[source_id] = source
    return source_id
```

### 6. Use Type Hints

Always use type hints for better IDE support:

```python
async def process(self, data: Dict[str, Any]) -> ProcessingResult:
    # Implementation
    pass
```

### 7. Document Your Implementations

Add docstrings to your implementations:

```python
class MyDataSource(IDataSource):
    """Custom data source for XYZ sensors.
    
    This data source connects to XYZ sensors via HTTP
    and collects temperature and humidity data.
    """
    
    async def connect(self) -> None:
        """Establish HTTP connection to the sensor."""
        # Implementation
        pass
```

---

## Support

For questions or issues, please refer to:
- Design document: `.kiro/specs/data-collector-interfaces/design.md`
- Requirements document: `.kiro/specs/data-collector-interfaces/requirements.md`
- Usage examples: `backend/src/collectors/examples.py`
