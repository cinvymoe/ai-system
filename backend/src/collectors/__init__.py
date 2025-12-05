"""Data Collector Module - Interface definitions for data collection, processing, and storage."""

from .enums import (
    CollectionStatus,
    TaskStatus,
    EventType,
    ErrorType,
)

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

from .interfaces import (
    IDataSource,
    IMetadataParser,
    ICollectionManager,
    IProcessor,
    IPipeline,
    IProcessingManager,
    IStorageBackend,
    IStorageManager,
    ICollectionLayerFactory,
    IProcessingLayerFactory,
    IStorageLayerFactory,
    IErrorHandler,
    IEventEmitter,
    ITaskTracker,
)

from .mocks import (
    MockDataSource,
    MockMetadataParser,
    MockProcessor,
    MockStorageBackend,
    MockErrorHandler,
    MockEventEmitter,
    MockTaskTracker,
)

__all__ = [
    # Enums
    "CollectionStatus",
    "TaskStatus",
    "EventType",
    "ErrorType",
    # Models
    "CollectedData",
    "ParsedMetadata",
    "CollectionTask",
    "CollectionStatistics",
    "ProcessingResult",
    "PipelineStep",
    "PipelineResult",
    "ProcessingStatistics",
    "StorageLocation",
    "QueryCriteria",
    "StorageStatistics",
    "ErrorInfo",
    "SystemEvent",
    "TaskInfo",
    # Collection Layer Interfaces
    "IDataSource",
    "IMetadataParser",
    "ICollectionManager",
    # Processing Layer Interfaces
    "IProcessor",
    "IPipeline",
    "IProcessingManager",
    # Storage Layer Interfaces
    "IStorageBackend",
    "IStorageManager",
    # Factory Interfaces
    "ICollectionLayerFactory",
    "IProcessingLayerFactory",
    "IStorageLayerFactory",
    # Cross-Cutting Interfaces
    "IErrorHandler",
    "IEventEmitter",
    "ITaskTracker",
    # Mock Implementations
    "MockDataSource",
    "MockMetadataParser",
    "MockProcessor",
    "MockStorageBackend",
    "MockErrorHandler",
    "MockEventEmitter",
    "MockTaskTracker",
]
