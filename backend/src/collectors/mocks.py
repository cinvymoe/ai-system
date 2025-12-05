"""Mock implementations for testing the Data Collector Module interfaces.

These mock implementations provide simple, in-memory versions of all interfaces
to support unit testing and integration testing without requiring real data sources,
processors, or storage backends.
"""

from datetime import datetime
from typing import Any, AsyncIterator, Callable, Dict, List, Optional
import uuid

from .interfaces.collection import IDataSource, IMetadataParser, ICollectionManager
from .interfaces.processing import IProcessor, IPipeline, IProcessingManager
from .interfaces.storage import IStorageBackend, IStorageManager
from .interfaces.crosscutting import IErrorHandler, IEventEmitter, ITaskTracker
from .models import (
    CollectedData,
    ParsedMetadata,
    CollectionTask,
    CollectionStatistics,
    ProcessingResult,
    PipelineStep,
    PipelineResult,
    ProcessingStatistics,
    StorageLocation,
    QueryCriteria,
    StorageStatistics,
    ErrorInfo,
    SystemEvent,
    TaskInfo,
)
from .enums import (
    CollectionStatus,
    TaskStatus,
    EventType,
    ErrorType,
)


class MockDataSource(IDataSource):
    """Mock data source for testing.
    
    Returns predefined data and tracks method calls for verification.
    """
    
    def __init__(self, source_id: str, data: bytes = b"mock_data"):
        """Initialize mock data source.
        
        Args:
            source_id: Unique identifier for this data source
            data: Data to return when collect() is called
        """
        self._source_id = source_id
        self._data = data
        self._connected = False
        self._collect_count = 0
        
    async def connect(self) -> None:
        """Establish connection to data source."""
        self._connected = True
        
    async def disconnect(self) -> None:
        """Disconnect from data source."""
        self._connected = False
        
    async def collect(self) -> CollectedData:
        """Collect single data sample."""
        if not self._connected:
            raise ConnectionError("Data source not connected")
        
        self._collect_count += 1
        return CollectedData(
            source_id=self._source_id,
            timestamp=datetime.now(),
            data_format="mock",
            collection_method="mock_collect",
            raw_data=self._data,
            metadata={"collect_count": self._collect_count}
        )
        
    async def collect_stream(self) -> AsyncIterator[CollectedData]:
        """Collect data stream."""
        if not self._connected:
            raise ConnectionError("Data source not connected")
        
        # Yield a few samples for testing
        for i in range(3):
            self._collect_count += 1
            yield CollectedData(
                source_id=self._source_id,
                timestamp=datetime.now(),
                data_format="mock",
                collection_method="mock_stream",
                raw_data=self._data,
                metadata={"collect_count": self._collect_count, "stream_index": i}
            )
            
    def get_source_id(self) -> str:
        """Get data source identifier."""
        return self._source_id
        
    # Test helper methods
    def is_connected(self) -> bool:
        """Check if data source is connected."""
        return self._connected
        
    def get_collect_count(self) -> int:
        """Get number of times collect was called."""
        return self._collect_count


class MockMetadataParser(IMetadataParser):
    """Mock metadata parser for testing."""
    
    def __init__(self, validation_result: bool = True):
        """Initialize mock metadata parser.
        
        Args:
            validation_result: Whether validation should pass or fail
        """
        self._validation_result = validation_result
        self._parse_count = 0
        
    async def parse(self, collected_data: CollectedData) -> ParsedMetadata:
        """Parse metadata from collected data."""
        self._parse_count += 1
        return ParsedMetadata(
            schema={"type": "mock", "version": "1.0"},
            quality_indicators={"completeness": 1.0, "accuracy": 0.95},
            source_attributes={"source_id": collected_data.source_id},
            is_valid=self._validation_result,
            validation_errors=[] if self._validation_result else ["Mock validation error"]
        )
        
    async def validate(self, metadata: ParsedMetadata) -> bool:
        """Validate metadata."""
        return metadata.is_valid
        
    # Test helper methods
    def get_parse_count(self) -> int:
        """Get number of times parse was called."""
        return self._parse_count


class MockProcessor(IProcessor):
    """Mock processor for testing.
    
    Performs simple data transformation and tracks processing calls.
    """
    
    def __init__(self, name: str, should_fail: bool = False):
        """Initialize mock processor.
        
        Args:
            name: Processor name
            should_fail: Whether processing should fail
        """
        self._name = name
        self._should_fail = should_fail
        self._process_count = 0
        
    async def process(self, data: Any) -> ProcessingResult:
        """Process data."""
        self._process_count += 1
        start_time = datetime.now()
        
        if self._should_fail:
            return ProcessingResult(
                success=False,
                processed_data=None,
                error=f"Mock processor {self._name} failed",
                processing_time=0.001
            )
        
        # Simple transformation: add processor name to data
        if isinstance(data, dict):
            processed = {**data, f"processed_by_{self._name}": True}
        else:
            processed = {"original": data, f"processed_by_{self._name}": True}
            
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return ProcessingResult(
            success=True,
            processed_data=processed,
            error=None,
            processing_time=processing_time
        )
        
    def get_processor_name(self) -> str:
        """Get processor name."""
        return self._name
        
    def validate_input(self, data: Any) -> bool:
        """Validate input data."""
        # Accept any data for testing
        return data is not None
        
    # Test helper methods
    def get_process_count(self) -> int:
        """Get number of times process was called."""
        return self._process_count


class MockStorageBackend(IStorageBackend):
    """Mock storage backend for testing.
    
    Uses in-memory storage and tracks all operations.
    """
    
    def __init__(self, backend_id: str):
        """Initialize mock storage backend.
        
        Args:
            backend_id: Unique identifier for this backend
        """
        self._backend_id = backend_id
        self._connected = False
        self._storage: Dict[str, Any] = {}
        self._store_count = 0
        
    async def connect(self) -> None:
        """Connect to storage backend."""
        self._connected = True
        
    async def disconnect(self) -> None:
        """Disconnect from storage backend."""
        self._connected = False
        
    async def store(self, data: Any) -> StorageLocation:
        """Store data."""
        if not self._connected:
            raise ConnectionError("Storage backend not connected")
        
        location_id = str(uuid.uuid4())
        self._storage[location_id] = data
        self._store_count += 1
        
        return StorageLocation(
            backend_id=self._backend_id,
            location_id=location_id,
            path=f"/mock/{self._backend_id}/{location_id}",
            created_at=datetime.now()
        )
        
    async def query(self, criteria: QueryCriteria) -> List[Any]:
        """Query data."""
        if not self._connected:
            raise ConnectionError("Storage backend not connected")
        
        # Simple filtering based on criteria
        results = list(self._storage.values())
        
        # Apply limit and offset
        if criteria.offset:
            results = results[criteria.offset:]
        if criteria.limit:
            results = results[:criteria.limit]
            
        return results
        
    async def delete(self, location_id: str) -> None:
        """Delete data."""
        if not self._connected:
            raise ConnectionError("Storage backend not connected")
        
        if location_id not in self._storage:
            raise KeyError(f"Location ID {location_id} not found")
        
        del self._storage[location_id]
        
    def get_backend_id(self) -> str:
        """Get backend identifier."""
        return self._backend_id
        
    # Test helper methods
    def is_connected(self) -> bool:
        """Check if backend is connected."""
        return self._connected
        
    def get_store_count(self) -> int:
        """Get number of times store was called."""
        return self._store_count
        
    def get_stored_data(self, location_id: str) -> Any:
        """Get stored data by location ID."""
        return self._storage.get(location_id)
        
    def get_all_stored_data(self) -> Dict[str, Any]:
        """Get all stored data."""
        return self._storage.copy()


class MockErrorHandler(IErrorHandler):
    """Mock error handler for testing.
    
    Records all errors for verification.
    """
    
    def __init__(self, handled_types: Optional[List[ErrorType]] = None):
        """Initialize mock error handler.
        
        Args:
            handled_types: List of error types this handler can handle.
                          If None, handles all types.
        """
        self._handled_types = handled_types
        self._handled_errors: List[ErrorInfo] = []
        
    async def handle_error(self, error: ErrorInfo) -> None:
        """Handle error."""
        if not self.can_handle(error.error_type):
            raise RuntimeError(f"Cannot handle error type {error.error_type}")
        
        self._handled_errors.append(error)
        
    def can_handle(self, error_type: ErrorType) -> bool:
        """Check if can handle error type."""
        if self._handled_types is None:
            return True
        return error_type in self._handled_types
        
    # Test helper methods
    def get_handled_errors(self) -> List[ErrorInfo]:
        """Get all handled errors."""
        return self._handled_errors.copy()
        
    def get_error_count(self) -> int:
        """Get number of errors handled."""
        return len(self._handled_errors)
        
    def clear_errors(self) -> None:
        """Clear recorded errors."""
        self._handled_errors.clear()


class MockEventEmitter(IEventEmitter):
    """Mock event emitter for testing.
    
    Records all emitted events and manages subscriptions.
    """
    
    def __init__(self):
        """Initialize mock event emitter."""
        self._emitted_events: List[SystemEvent] = []
        self._subscriptions: Dict[str, tuple[EventType, Callable]] = {}
        
    async def emit(self, event: SystemEvent) -> None:
        """Emit event."""
        self._emitted_events.append(event)
        
        # Call all subscribed handlers
        for sub_id, (event_type, handler) in self._subscriptions.items():
            if event_type == event.event_type:
                if callable(handler):
                    # Call handler (may be sync or async)
                    result = handler(event)
                    if hasattr(result, '__await__'):
                        await result
                        
    async def subscribe(self, event_type: EventType, handler: Callable) -> str:
        """Subscribe to event."""
        if not callable(handler):
            raise ValueError("Handler must be callable")
        
        subscription_id = str(uuid.uuid4())
        self._subscriptions[subscription_id] = (event_type, handler)
        return subscription_id
        
    async def unsubscribe(self, subscription_id: str) -> None:
        """Unsubscribe from event."""
        if subscription_id not in self._subscriptions:
            raise KeyError(f"Subscription ID {subscription_id} not found")
        
        del self._subscriptions[subscription_id]
        
    # Test helper methods
    def get_emitted_events(self) -> List[SystemEvent]:
        """Get all emitted events."""
        return self._emitted_events.copy()
        
    def get_event_count(self, event_type: Optional[EventType] = None) -> int:
        """Get count of emitted events, optionally filtered by type."""
        if event_type is None:
            return len(self._emitted_events)
        return sum(1 for e in self._emitted_events if e.event_type == event_type)
        
    def clear_events(self) -> None:
        """Clear recorded events."""
        self._emitted_events.clear()
        
    def get_subscription_count(self) -> int:
        """Get number of active subscriptions."""
        return len(self._subscriptions)


class MockTaskTracker(ITaskTracker):
    """Mock task tracker for testing.
    
    Tracks all tasks and their state changes.
    """
    
    def __init__(self):
        """Initialize mock task tracker."""
        self._tasks: Dict[str, TaskInfo] = {}
        
    async def create_task(self, task_type: str) -> str:
        """Create task."""
        task_id = str(uuid.uuid4())
        self._tasks[task_id] = TaskInfo(
            task_id=task_id,
            task_type=task_type,
            status=TaskStatus.PENDING,
            created_at=datetime.now(),
            started_at=None,
            completed_at=None,
            progress=0.0,
            result=None,
            error=None
        )
        return task_id
        
    async def update_status(self, task_id: str, status: TaskStatus) -> None:
        """Update task status."""
        if task_id not in self._tasks:
            raise KeyError(f"Task ID {task_id} not found")
        
        task = self._tasks[task_id]
        task.status = status
        
        if status == TaskStatus.RUNNING and task.started_at is None:
            task.started_at = datetime.now()
        elif status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED):
            task.completed_at = datetime.now()
            
    async def update_progress(self, task_id: str, progress: float) -> None:
        """Update task progress."""
        if task_id not in self._tasks:
            raise KeyError(f"Task ID {task_id} not found")
        
        if not 0.0 <= progress <= 1.0:
            raise ValueError(f"Progress must be between 0.0 and 1.0, got {progress}")
        
        self._tasks[task_id].progress = progress
        
    async def get_task_info(self, task_id: str) -> TaskInfo:
        """Get task information."""
        if task_id not in self._tasks:
            raise KeyError(f"Task ID {task_id} not found")
        
        return self._tasks[task_id]
        
    async def cancel_task(self, task_id: str) -> None:
        """Cancel task."""
        if task_id not in self._tasks:
            raise KeyError(f"Task ID {task_id} not found")
        
        task = self._tasks[task_id]
        if task.status in (TaskStatus.COMPLETED, TaskStatus.FAILED):
            raise RuntimeError(f"Cannot cancel task in {task.status} state")
        
        await self.update_status(task_id, TaskStatus.CANCELLED)
        
    # Test helper methods
    def get_all_tasks(self) -> Dict[str, TaskInfo]:
        """Get all tasks."""
        return self._tasks.copy()
        
    def get_task_count(self, status: Optional[TaskStatus] = None) -> int:
        """Get count of tasks, optionally filtered by status."""
        if status is None:
            return len(self._tasks)
        return sum(1 for t in self._tasks.values() if t.status == status)
        
    def clear_tasks(self) -> None:
        """Clear all tasks."""
        self._tasks.clear()
