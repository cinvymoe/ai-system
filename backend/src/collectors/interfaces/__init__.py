"""Interface definitions for the Data Collector Module."""

from .collection import (
    IDataSource,
    IMetadataParser,
    ICollectionManager,
)
from .processing import (
    IProcessor,
    IPipeline,
    IProcessingManager,
)
from .storage import (
    IStorageBackend,
    IStorageManager,
)
from .factories import (
    ICollectionLayerFactory,
    IProcessingLayerFactory,
    IStorageLayerFactory,
)
from .crosscutting import (
    IErrorHandler,
    IEventEmitter,
    ITaskTracker,
)

__all__ = [
    "IDataSource",
    "IMetadataParser",
    "ICollectionManager",
    "IProcessor",
    "IPipeline",
    "IProcessingManager",
    "IStorageBackend",
    "IStorageManager",
    "ICollectionLayerFactory",
    "IProcessingLayerFactory",
    "IStorageLayerFactory",
    "IErrorHandler",
    "IEventEmitter",
    "ITaskTracker",
]
