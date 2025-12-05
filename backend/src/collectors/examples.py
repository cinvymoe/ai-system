"""Usage examples for the Data Collector Module interfaces.

This module demonstrates how to use the data collector interfaces to build
a complete data collection, processing, and storage pipeline.
"""

import asyncio
from datetime import datetime
from typing import Any, Dict

from .interfaces import (
    IDataSource,
    IProcessor,
    IStorageBackend,
    IErrorHandler,
    IEventEmitter,
)
from .models import (
    CollectedData,
    ProcessingResult,
    StorageLocation,
    ErrorInfo,
    SystemEvent,
)
from .enums import ErrorType, EventType
from .mocks import (
    MockDataSource,
    MockProcessor,
    MockStorageBackend,
    MockErrorHandler,
    MockEventEmitter,
)


# Example 1: Basic Data Collection
# =================================

async def example_basic_collection():
    """Example: Collect data from a single source."""
    print("\n=== Example 1: Basic Data Collection ===\n")
    
    # Create a data source
    source = MockDataSource(source_id="sensor_001", data=b"temperature:25.5")
    
    # Connect to the source
    await source.connect()
    print(f"Connected to data source: {source.get_source_id()}")
    
    # Collect a single data sample
    data = await source.collect()
    print(f"Collected data:")
    print(f"  - Source ID: {data.source_id}")
    print(f"  - Timestamp: {data.timestamp}")
    print(f"  - Format: {data.data_format}")
    print(f"  - Raw data: {data.raw_data.decode()}")
    print(f"  - Metadata: {data.metadata}")
    
    # Disconnect from the source
    await source.disconnect()
    print("Disconnected from data source")


# Example 2: Stream Data Collection
# ==================================

async def example_stream_collection():
    """Example: Collect streaming data from a source."""
    print("\n=== Example 2: Stream Data Collection ===\n")
    
    source = MockDataSource(source_id="sensor_002", data=b"pressure:101.3")
    await source.connect()
    
    print(f"Collecting stream from: {source.get_source_id()}")
    
    # Collect data stream
    async for data in source.collect_stream():
        print(f"Stream sample {data.metadata['stream_index']}:")
        print(f"  - Timestamp: {data.timestamp}")
        print(f"  - Data: {data.raw_data.decode()}")
    
    await source.disconnect()


# Example 3: Data Processing Pipeline
# ====================================

async def example_processing_pipeline():
    """Example: Process data through multiple processors."""
    print("\n=== Example 3: Data Processing Pipeline ===\n")
    
    # Create processors
    validator = MockProcessor(name="validator")
    transformer = MockProcessor(name="transformer")
    enricher = MockProcessor(name="enricher")
    
    # Initial data
    input_data = {"sensor_id": "sensor_003", "value": 42.0}
    print(f"Input data: {input_data}")
    
    # Process through pipeline
    result1 = await validator.process(input_data)
    if result1.success:
        print(f"After validation: {result1.processed_data}")
        
        result2 = await transformer.process(result1.processed_data)
        if result2.success:
            print(f"After transformation: {result2.processed_data}")
            
            result3 = await enricher.process(result2.processed_data)
            if result3.success:
                print(f"Final result: {result3.processed_data}")
                print(f"Total processing time: {result1.processing_time + result2.processing_time + result3.processing_time:.4f}s")


# Example 4: Data Storage
# =======================

async def example_data_storage():
    """Example: Store and query data."""
    print("\n=== Example 4: Data Storage ===\n")
    
    # Create storage backend
    storage = MockStorageBackend(backend_id="db_001")
    await storage.connect()
    print(f"Connected to storage backend: {storage.get_backend_id()}")
    
    # Store multiple data items
    data_items = [
        {"sensor": "temp_01", "value": 25.5, "unit": "celsius"},
        {"sensor": "temp_02", "value": 26.2, "unit": "celsius"},
        {"sensor": "pressure_01", "value": 101.3, "unit": "kPa"},
    ]
    
    locations = []
    for item in data_items:
        location = await storage.store(item)
        locations.append(location)
        print(f"Stored {item['sensor']}: {location.location_id}")
    
    # Query stored data
    from .models import QueryCriteria
    criteria = QueryCriteria(
        filters={},
        sort_by=None,
        limit=2,
        offset=0
    )
    
    results = await storage.query(criteria)
    print(f"\nQueried {len(results)} items (limit=2):")
    for result in results:
        print(f"  - {result}")
    
    await storage.disconnect()


# Example 5: Error Handling
# =========================

async def example_error_handling():
    """Example: Handle errors with error handlers."""
    print("\n=== Example 5: Error Handling ===\n")
    
    # Create error handler
    error_handler = MockErrorHandler(handled_types=[ErrorType.VALIDATION, ErrorType.PROCESSING])
    
    # Simulate various errors
    errors = [
        ErrorInfo(
            error_type=ErrorType.VALIDATION,
            timestamp=datetime.now(),
            layer_name="processing",
            operation="validate_input",
            message="Invalid data format",
            details={"expected": "dict", "got": "str"},
            is_critical=False
        ),
        ErrorInfo(
            error_type=ErrorType.PROCESSING,
            timestamp=datetime.now(),
            layer_name="processing",
            operation="transform_data",
            message="Transformation failed",
            details={"step": "normalize", "reason": "division by zero"},
            is_critical=True
        ),
    ]
    
    for error in errors:
        if error_handler.can_handle(error.error_type):
            await error_handler.handle_error(error)
            print(f"Handled {error.error_type.value} error: {error.message}")
        else:
            print(f"Cannot handle {error.error_type.value} error")
    
    print(f"\nTotal errors handled: {error_handler.get_error_count()}")


# Example 6: Event System
# =======================

async def example_event_system():
    """Example: Use event emitter for system notifications."""
    print("\n=== Example 6: Event System ===\n")
    
    # Create event emitter
    emitter = MockEventEmitter()
    
    # Define event handlers
    async def on_collection_start(event: SystemEvent):
        print(f"[Handler] Collection started: {event.data.get('source_id')}")
    
    async def on_collection_complete(event: SystemEvent):
        print(f"[Handler] Collection completed: {event.data.get('items_collected')} items")
    
    # Subscribe to events
    sub1 = await emitter.subscribe(EventType.COLLECTION_START, on_collection_start)
    sub2 = await emitter.subscribe(EventType.COLLECTION_COMPLETE, on_collection_complete)
    
    print("Subscribed to collection events")
    
    # Emit events
    await emitter.emit(SystemEvent(
        event_type=EventType.COLLECTION_START,
        timestamp=datetime.now(),
        source="collection_manager",
        data={"source_id": "sensor_001", "task_id": "task_123"}
    ))
    
    await emitter.emit(SystemEvent(
        event_type=EventType.COLLECTION_COMPLETE,
        timestamp=datetime.now(),
        source="collection_manager",
        data={"source_id": "sensor_001", "items_collected": 100}
    ))
    
    print(f"\nTotal events emitted: {emitter.get_event_count()}")
    
    # Unsubscribe
    await emitter.unsubscribe(sub1)
    await emitter.unsubscribe(sub2)


# Example 7: Complete End-to-End Pipeline
# ========================================

async def example_complete_pipeline():
    """Example: Complete data collection, processing, and storage pipeline."""
    print("\n=== Example 7: Complete End-to-End Pipeline ===\n")
    
    # Setup components
    source = MockDataSource(source_id="sensor_complete", data=b"humidity:65.5")
    processor = MockProcessor(name="normalizer")
    storage = MockStorageBackend(backend_id="main_db")
    emitter = MockEventEmitter()
    error_handler = MockErrorHandler()
    
    # Event handler for monitoring
    async def log_event(event: SystemEvent):
        print(f"[Event] {event.event_type.value} at {event.timestamp.strftime('%H:%M:%S')}")
    
    await emitter.subscribe(EventType.COLLECTION_START, log_event)
    await emitter.subscribe(EventType.PROCESSING_COMPLETE, log_event)
    await emitter.subscribe(EventType.STORAGE_COMPLETE, log_event)
    
    try:
        # Step 1: Collection
        await emitter.emit(SystemEvent(
            event_type=EventType.COLLECTION_START,
            timestamp=datetime.now(),
            source="pipeline",
            data={"source_id": source.get_source_id()}
        ))
        
        await source.connect()
        collected_data = await source.collect()
        print(f"\n1. Collected: {collected_data.raw_data.decode()}")
        
        # Step 2: Processing
        processing_result = await processor.process({
            "raw": collected_data.raw_data.decode(),
            "source": collected_data.source_id,
            "timestamp": collected_data.timestamp.isoformat()
        })
        
        if processing_result.success:
            print(f"2. Processed: {processing_result.processed_data}")
            
            await emitter.emit(SystemEvent(
                event_type=EventType.PROCESSING_COMPLETE,
                timestamp=datetime.now(),
                source="pipeline",
                data={"success": True}
            ))
        else:
            raise ValueError(f"Processing failed: {processing_result.error}")
        
        # Step 3: Storage
        await storage.connect()
        location = await storage.store(processing_result.processed_data)
        print(f"3. Stored at: {location.path}")
        
        await emitter.emit(SystemEvent(
            event_type=EventType.STORAGE_COMPLETE,
            timestamp=datetime.now(),
            source="pipeline",
            data={"location_id": location.location_id}
        ))
        
        print("\n✓ Pipeline completed successfully")
        
    except Exception as e:
        # Handle errors
        error = ErrorInfo(
            error_type=ErrorType.PROCESSING,
            timestamp=datetime.now(),
            layer_name="pipeline",
            operation="execute",
            message=str(e),
            details={"exception_type": type(e).__name__},
            is_critical=True
        )
        await error_handler.handle_error(error)
        print(f"\n✗ Pipeline failed: {e}")
        
    finally:
        # Cleanup
        await source.disconnect()
        await storage.disconnect()


# Example 8: Custom Data Source Implementation
# ============================================

class CustomSensorDataSource(IDataSource):
    """Example custom data source implementation.
    
    This demonstrates how to implement the IDataSource interface
    for a real sensor or data source.
    """
    
    def __init__(self, sensor_id: str, sensor_url: str):
        """Initialize custom sensor data source.
        
        Args:
            sensor_id: Unique sensor identifier
            sensor_url: URL or connection string for the sensor
        """
        self._sensor_id = sensor_id
        self._sensor_url = sensor_url
        self._connected = False
    
    async def connect(self) -> None:
        """Connect to the sensor."""
        # In a real implementation, establish connection to sensor
        print(f"Connecting to sensor at {self._sensor_url}...")
        # await sensor_client.connect(self._sensor_url)
        self._connected = True
        print("Connected!")
    
    async def disconnect(self) -> None:
        """Disconnect from the sensor."""
        # In a real implementation, close connection
        print("Disconnecting from sensor...")
        # await sensor_client.disconnect()
        self._connected = False
        print("Disconnected!")
    
    async def collect(self) -> CollectedData:
        """Collect data from the sensor."""
        if not self._connected:
            raise ConnectionError("Sensor not connected")
        
        # In a real implementation, read from sensor
        # sensor_reading = await sensor_client.read()
        sensor_reading = b"simulated_sensor_data"
        
        return CollectedData(
            source_id=self._sensor_id,
            timestamp=datetime.now(),
            data_format="sensor_binary",
            collection_method="http_get",
            raw_data=sensor_reading,
            metadata={
                "sensor_url": self._sensor_url,
                "protocol": "http",
                "version": "1.0"
            }
        )
    
    async def collect_stream(self):
        """Collect streaming data from the sensor."""
        if not self._connected:
            raise ConnectionError("Sensor not connected")
        
        # In a real implementation, stream from sensor
        while self._connected:
            yield await self.collect()
            await asyncio.sleep(1.0)  # Poll every second
    
    def get_source_id(self) -> str:
        """Get sensor identifier."""
        return self._sensor_id


async def example_custom_data_source():
    """Example: Use a custom data source implementation."""
    print("\n=== Example 8: Custom Data Source Implementation ===\n")
    
    # Create custom data source
    sensor = CustomSensorDataSource(
        sensor_id="custom_sensor_001",
        sensor_url="http://sensor.example.com/api/v1/data"
    )
    
    # Use it like any other data source
    await sensor.connect()
    data = await sensor.collect()
    
    print(f"Collected from custom sensor:")
    print(f"  - Source ID: {data.source_id}")
    print(f"  - Method: {data.collection_method}")
    print(f"  - Metadata: {data.metadata}")
    
    await sensor.disconnect()


# Main function to run all examples
# ==================================

async def run_all_examples():
    """Run all usage examples."""
    examples = [
        example_basic_collection,
        example_stream_collection,
        example_processing_pipeline,
        example_data_storage,
        example_error_handling,
        example_event_system,
        example_complete_pipeline,
        example_custom_data_source,
    ]
    
    for example in examples:
        try:
            await example()
        except Exception as e:
            print(f"\nExample failed with error: {e}")
        
        # Pause between examples
        await asyncio.sleep(0.5)
    
    print("\n" + "="*50)
    print("All examples completed!")
    print("="*50)


if __name__ == "__main__":
    # Run all examples
    asyncio.run(run_all_examples())
