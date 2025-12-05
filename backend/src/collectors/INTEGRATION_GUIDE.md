# Data Collector Module - Integration Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Architecture Overview](#architecture-overview)
3. [Getting Started](#getting-started)
4. [Implementing Custom Components](#implementing-custom-components)
5. [Integration Patterns](#integration-patterns)
6. [Testing Your Integration](#testing-your-integration)
7. [Production Deployment](#production-deployment)
8. [Troubleshooting](#troubleshooting)

---

## Introduction

This guide will help you integrate the Data Collector Module into your application. Whether you're building a simple data collection pipeline or a complex multi-source data processing system, this guide provides step-by-step instructions and best practices.

### What You'll Learn

- How to implement custom data sources, processors, and storage backends
- How to build complete data pipelines
- How to handle errors and monitor your system
- How to test your integration
- How to deploy to production

### Prerequisites

- Python 3.10 or higher
- Basic understanding of async/await in Python
- Familiarity with your data sources and storage systems

---

## Architecture Overview

The Data Collector Module uses a three-layer architecture:

```
┌─────────────────────────────────────────────────────────┐
│                    Your Application                      │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│              Data Collection Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Data Source  │  │ Data Source  │  │ Data Source  │ │
│  │      1       │  │      2       │  │      N       │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│              Data Processing Layer                       │
│  ┌──────────────────────────────────────────────────┐  │
│  │              Processing Pipeline                  │  │
│  │  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐        │  │
│  │  │Step 1│→ │Step 2│→ │Step 3│→ │Step N│        │  │
│  │  └──────┘  └──────┘  └──────┘  └──────┘        │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│              Data Storage Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Storage    │  │   Storage    │  │   Storage    │ │
│  │  Backend 1   │  │  Backend 2   │  │  Backend N   │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Key Concepts

- **Data Source**: Represents any source of data (sensors, APIs, databases, files)
- **Processor**: Transforms, validates, or enriches data
- **Pipeline**: A sequence of processors that execute in order
- **Storage Backend**: Persists processed data to a storage system
- **Manager**: Coordinates components within each layer

---

## Getting Started

### Step 1: Install Dependencies

Ensure you have the backend package installed:

```bash
cd backend
pip install -e .
```

### Step 2: Import Required Interfaces

```python
from collectors.interfaces import (
    IDataSource,
    IProcessor,
    IStorageBackend,
    ICollectionManager,
    IProcessingManager,
    IStorageManager,
)
from collectors.models import (
    CollectedData,
    ProcessingResult,
    StorageLocation,
)
from collectors.enums import CollectionStatus, TaskStatus
```

### Step 3: Use Mock Implementations for Testing

Start with mock implementations to understand the flow:

```python
from collectors.mocks import (
    MockDataSource,
    MockProcessor,
    MockStorageBackend,
)

async def test_pipeline():
    # Create mock components
    source = MockDataSource(source_id="test_source", data=b"test_data")
    processor = MockProcessor(name="test_processor")
    storage = MockStorageBackend(backend_id="test_storage")
    
    # Connect
    await source.connect()
    await storage.connect()
    
    # Collect, process, store
    data = await source.collect()
    result = await processor.process({"raw": data.raw_data})
    location = await storage.store(result.processed_data)
    
    print(f"Data stored at: {location.path}")
    
    # Cleanup
    await source.disconnect()
    await storage.disconnect()
```

---

## Implementing Custom Components

### Implementing a Custom Data Source

Here's how to implement a data source for an HTTP API:

```python
import aiohttp
from datetime import datetime
from typing import AsyncIterator
from collectors.interfaces import IDataSource
from collectors.models import CollectedData

class HTTPAPIDataSource(IDataSource):
    """Data source that collects data from an HTTP API."""
    
    def __init__(self, source_id: str, api_url: str, api_key: str):
        """Initialize HTTP API data source.
        
        Args:
            source_id: Unique identifier for this source
            api_url: Base URL of the API
            api_key: API authentication key
        """
        self._source_id = source_id
        self._api_url = api_url
        self._api_key = api_key
        self._session = None
    
    async def connect(self) -> None:
        """Create HTTP session."""
        self._session = aiohttp.ClientSession(
            headers={"Authorization": f"Bearer {self._api_key}"}
        )
    
    async def disconnect(self) -> None:
        """Close HTTP session."""
        if self._session:
            await self._session.close()
            self._session = None
    
    async def collect(self) -> CollectedData:
        """Collect data from API endpoint."""
        if not self._session:
            raise ConnectionError("Data source not connected")
        
        async with self._session.get(f"{self._api_url}/data") as response:
            if response.status != 200:
                raise ValueError(f"API returned status {response.status}")
            
            raw_data = await response.read()
            
            return CollectedData(
                source_id=self._source_id,
                timestamp=datetime.now(),
                data_format="json",
                collection_method="http_get",
                raw_data=raw_data,
                metadata={
                    "api_url": self._api_url,
                    "status_code": response.status,
                    "content_type": response.content_type,
                }
            )
    
    async def collect_stream(self) -> AsyncIterator[CollectedData]:
        """Collect streaming data from API."""
        if not self._session:
            raise ConnectionError("Data source not connected")
        
        # For WebSocket or SSE streaming
        async with self._session.ws_connect(f"{self._api_url}/stream") as ws:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    yield CollectedData(
                        source_id=self._source_id,
                        timestamp=datetime.now(),
                        data_format="json",
                        collection_method="websocket",
                        raw_data=msg.data.encode(),
                        metadata={"message_type": "text"}
                    )
    
    def get_source_id(self) -> str:
        """Get source identifier."""
        return self._source_id
```

### Implementing a Custom Processor

Here's how to implement a data validation processor:

```python
import json
from typing import Any
from collectors.interfaces import IProcessor
from collectors.models import ProcessingResult
from datetime import datetime

class JSONValidationProcessor(IProcessor):
    """Processor that validates and parses JSON data."""
    
    def __init__(self, name: str, required_fields: list[str]):
        """Initialize JSON validation processor.
        
        Args:
            name: Processor name
            required_fields: List of required field names
        """
        self._name = name
        self._required_fields = required_fields
    
    async def process(self, data: Any) -> ProcessingResult:
        """Validate and parse JSON data."""
        start_time = datetime.now()
        
        try:
            # Parse JSON if it's bytes or string
            if isinstance(data, bytes):
                parsed = json.loads(data.decode())
            elif isinstance(data, str):
                parsed = json.loads(data)
            elif isinstance(data, dict):
                parsed = data
            else:
                return ProcessingResult(
                    success=False,
                    processed_data=None,
                    error=f"Invalid data type: {type(data)}",
                    processing_time=0.0
                )
            
            # Validate required fields
            missing_fields = [
                field for field in self._required_fields
                if field not in parsed
            ]
            
            if missing_fields:
                return ProcessingResult(
                    success=False,
                    processed_data=None,
                    error=f"Missing required fields: {missing_fields}",
                    processing_time=(datetime.now() - start_time).total_seconds()
                )
            
            # Add validation metadata
            parsed["_validated"] = True
            parsed["_validated_at"] = datetime.now().isoformat()
            
            return ProcessingResult(
                success=True,
                processed_data=parsed,
                error=None,
                processing_time=(datetime.now() - start_time).total_seconds()
            )
            
        except json.JSONDecodeError as e:
            return ProcessingResult(
                success=False,
                processed_data=None,
                error=f"JSON decode error: {str(e)}",
                processing_time=(datetime.now() - start_time).total_seconds()
            )
    
    def get_processor_name(self) -> str:
        """Get processor name."""
        return self._name
    
    def validate_input(self, data: Any) -> bool:
        """Validate input data."""
        return data is not None
```

### Implementing a Custom Storage Backend

Here's how to implement a PostgreSQL storage backend:

```python
import asyncpg
from datetime import datetime
from typing import Any, List, Dict
from collectors.interfaces import IStorageBackend
from collectors.models import StorageLocation, QueryCriteria

class PostgreSQLStorageBackend(IStorageBackend):
    """Storage backend for PostgreSQL database."""
    
    def __init__(self, backend_id: str, connection_string: str, table_name: str):
        """Initialize PostgreSQL storage backend.
        
        Args:
            backend_id: Unique backend identifier
            connection_string: PostgreSQL connection string
            table_name: Name of the table to store data
        """
        self._backend_id = backend_id
        self._connection_string = connection_string
        self._table_name = table_name
        self._pool = None
    
    async def connect(self) -> None:
        """Create connection pool."""
        self._pool = await asyncpg.create_pool(self._connection_string)
        
        # Create table if it doesn't exist
        async with self._pool.acquire() as conn:
            await conn.execute(f"""
                CREATE TABLE IF NOT EXISTS {self._table_name} (
                    id SERIAL PRIMARY KEY,
                    location_id UUID UNIQUE NOT NULL,
                    data JSONB NOT NULL,
                    created_at TIMESTAMP NOT NULL
                )
            """)
    
    async def disconnect(self) -> None:
        """Close connection pool."""
        if self._pool:
            await self._pool.close()
            self._pool = None
    
    async def store(self, data: Any) -> StorageLocation:
        """Store data to PostgreSQL."""
        if not self._pool:
            raise ConnectionError("Storage backend not connected")
        
        import uuid
        import json
        
        location_id = str(uuid.uuid4())
        created_at = datetime.now()
        
        async with self._pool.acquire() as conn:
            await conn.execute(
                f"""
                INSERT INTO {self._table_name} (location_id, data, created_at)
                VALUES ($1, $2, $3)
                """,
                location_id,
                json.dumps(data),
                created_at
            )
        
        return StorageLocation(
            backend_id=self._backend_id,
            location_id=location_id,
            path=f"postgresql://{self._table_name}/{location_id}",
            created_at=created_at
        )
    
    async def query(self, criteria: QueryCriteria) -> List[Any]:
        """Query data from PostgreSQL."""
        if not self._pool:
            raise ConnectionError("Storage backend not connected")
        
        import json
        
        # Build query
        query = f"SELECT data FROM {self._table_name} WHERE 1=1"
        params = []
        
        # Add filters (simplified example)
        for key, value in criteria.filters.items():
            params.append(value)
            query += f" AND data->>{len(params)} = ${len(params)}"
        
        # Add sorting
        if criteria.sort_by:
            query += f" ORDER BY data->>'{criteria.sort_by}'"
        
        # Add limit and offset
        if criteria.limit:
            params.append(criteria.limit)
            query += f" LIMIT ${len(params)}"
        
        if criteria.offset:
            params.append(criteria.offset)
            query += f" OFFSET ${len(params)}"
        
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
            return [json.loads(row['data']) for row in rows]
    
    async def delete(self, location_id: str) -> None:
        """Delete data from PostgreSQL."""
        if not self._pool:
            raise ConnectionError("Storage backend not connected")
        
        async with self._pool.acquire() as conn:
            result = await conn.execute(
                f"DELETE FROM {self._table_name} WHERE location_id = $1",
                location_id
            )
            
            if result == "DELETE 0":
                raise KeyError(f"Location ID {location_id} not found")
    
    def get_backend_id(self) -> str:
        """Get backend identifier."""
        return self._backend_id
```

---

## Integration Patterns

### Pattern 1: Simple Pipeline

For basic data collection and storage:

```python
async def simple_pipeline():
    """Simple collect-store pipeline."""
    source = HTTPAPIDataSource(
        source_id="api_001",
        api_url="https://api.example.com",
        api_key="your_api_key"
    )
    storage = PostgreSQLStorageBackend(
        backend_id="postgres_001",
        connection_string="postgresql://user:pass@localhost/db",
        table_name="collected_data"
    )
    
    await source.connect()
    await storage.connect()
    
    try:
        # Collect and store
        data = await source.collect()
        location = await storage.store({
            "source_id": data.source_id,
            "timestamp": data.timestamp.isoformat(),
            "raw_data": data.raw_data.decode(),
            "metadata": data.metadata
        })
        print(f"Stored at: {location.path}")
    finally:
        await source.disconnect()
        await storage.disconnect()
```

### Pattern 2: Processing Pipeline

For data transformation before storage:

```python
async def processing_pipeline():
    """Collect-process-store pipeline."""
    source = HTTPAPIDataSource(...)
    validator = JSONValidationProcessor(
        name="validator",
        required_fields=["sensor_id", "value", "timestamp"]
    )
    storage = PostgreSQLStorageBackend(...)
    
    await source.connect()
    await storage.connect()
    
    try:
        # Collect
        data = await source.collect()
        
        # Process
        result = await validator.process(data.raw_data)
        if not result.success:
            print(f"Validation failed: {result.error}")
            return
        
        # Store
        location = await storage.store(result.processed_data)
        print(f"Stored at: {location.path}")
    finally:
        await source.disconnect()
        await storage.disconnect()
```

### Pattern 3: Multi-Source Pipeline

For collecting from multiple sources:

```python
async def multi_source_pipeline():
    """Collect from multiple sources."""
    sources = [
        HTTPAPIDataSource("api_001", "https://api1.example.com", "key1"),
        HTTPAPIDataSource("api_002", "https://api2.example.com", "key2"),
        HTTPAPIDataSource("api_003", "https://api3.example.com", "key3"),
    ]
    storage = PostgreSQLStorageBackend(...)
    
    # Connect all sources
    await asyncio.gather(*[source.connect() for source in sources])
    await storage.connect()
    
    try:
        # Collect from all sources concurrently
        collected_data = await asyncio.gather(
            *[source.collect() for source in sources]
        )
        
        # Store all data
        locations = await asyncio.gather(
            *[storage.store({
                "source_id": data.source_id,
                "raw_data": data.raw_data.decode(),
                "timestamp": data.timestamp.isoformat()
            }) for data in collected_data]
        )
        
        print(f"Stored {len(locations)} items")
    finally:
        await asyncio.gather(*[source.disconnect() for source in sources])
        await storage.disconnect()
```

### Pattern 4: Event-Driven Pipeline

For monitoring and notifications:

```python
from collectors.mocks import MockEventEmitter
from collectors.enums import EventType
from collectors.models import SystemEvent

async def event_driven_pipeline():
    """Pipeline with event monitoring."""
    source = HTTPAPIDataSource(...)
    storage = PostgreSQLStorageBackend(...)
    emitter = MockEventEmitter()
    
    # Subscribe to events
    async def on_collection_complete(event: SystemEvent):
        print(f"[Event] Collection completed: {event.data}")
    
    async def on_storage_complete(event: SystemEvent):
        print(f"[Event] Storage completed: {event.data}")
    
    await emitter.subscribe(EventType.COLLECTION_COMPLETE, on_collection_complete)
    await emitter.subscribe(EventType.STORAGE_COMPLETE, on_storage_complete)
    
    await source.connect()
    await storage.connect()
    
    try:
        # Collect
        data = await source.collect()
        await emitter.emit(SystemEvent(
            event_type=EventType.COLLECTION_COMPLETE,
            timestamp=datetime.now(),
            source="pipeline",
            data={"source_id": data.source_id, "size": len(data.raw_data)}
        ))
        
        # Store
        location = await storage.store({"data": data.raw_data.decode()})
        await emitter.emit(SystemEvent(
            event_type=EventType.STORAGE_COMPLETE,
            timestamp=datetime.now(),
            source="pipeline",
            data={"location_id": location.location_id}
        ))
    finally:
        await source.disconnect()
        await storage.disconnect()
```

### Pattern 5: Error Handling Pipeline

For robust error handling:

```python
from collectors.mocks import MockErrorHandler
from collectors.models import ErrorInfo
from collectors.enums import ErrorType

async def error_handling_pipeline():
    """Pipeline with comprehensive error handling."""
    source = HTTPAPIDataSource(...)
    storage = PostgreSQLStorageBackend(...)
    error_handler = MockErrorHandler()
    
    await source.connect()
    await storage.connect()
    
    try:
        # Collect with error handling
        try:
            data = await source.collect()
        except ConnectionError as e:
            error = ErrorInfo(
                error_type=ErrorType.CONNECTION,
                timestamp=datetime.now(),
                layer_name="collection",
                operation="collect",
                message=str(e),
                details={"source_id": source.get_source_id()},
                is_critical=True
            )
            await error_handler.handle_error(error)
            return
        
        # Store with error handling
        try:
            location = await storage.store({"data": data.raw_data.decode()})
            print(f"Success: {location.path}")
        except Exception as e:
            error = ErrorInfo(
                error_type=ErrorType.STORAGE,
                timestamp=datetime.now(),
                layer_name="storage",
                operation="store",
                message=str(e),
                details={"backend_id": storage.get_backend_id()},
                is_critical=True
            )
            await error_handler.handle_error(error)
    finally:
        await source.disconnect()
        await storage.disconnect()
```

---

## Testing Your Integration

### Unit Testing

Test individual components:

```python
import pytest
from your_module import HTTPAPIDataSource

@pytest.mark.asyncio
async def test_http_data_source_connect():
    """Test data source connection."""
    source = HTTPAPIDataSource(
        source_id="test",
        api_url="https://api.example.com",
        api_key="test_key"
    )
    
    await source.connect()
    assert source._session is not None
    
    await source.disconnect()
    assert source._session is None

@pytest.mark.asyncio
async def test_http_data_source_collect():
    """Test data collection."""
    source = HTTPAPIDataSource(...)
    await source.connect()
    
    data = await source.collect()
    assert data.source_id == "test"
    assert data.raw_data is not None
    
    await source.disconnect()
```

### Integration Testing

Test complete pipelines:

```python
@pytest.mark.asyncio
async def test_complete_pipeline():
    """Test end-to-end pipeline."""
    source = HTTPAPIDataSource(...)
    processor = JSONValidationProcessor(...)
    storage = PostgreSQLStorageBackend(...)
    
    await source.connect()
    await storage.connect()
    
    try:
        # Collect
        data = await source.collect()
        assert data is not None
        
        # Process
        result = await processor.process(data.raw_data)
        assert result.success
        
        # Store
        location = await storage.store(result.processed_data)
        assert location.location_id is not None
        
        # Query back
        from collectors.models import QueryCriteria
        criteria = QueryCriteria(filters={}, sort_by=None, limit=1, offset=0)
        results = await storage.query(criteria)
        assert len(results) > 0
    finally:
        await source.disconnect()
        await storage.disconnect()
```

---

## Production Deployment

### Configuration Management

Use environment variables for configuration:

```python
import os

class Config:
    """Production configuration."""
    
    # Data source configuration
    API_URL = os.getenv("API_URL", "https://api.example.com")
    API_KEY = os.getenv("API_KEY")
    
    # Storage configuration
    DB_CONNECTION = os.getenv("DATABASE_URL")
    DB_TABLE = os.getenv("DB_TABLE", "collected_data")
    
    # Monitoring
    ENABLE_EVENTS = os.getenv("ENABLE_EVENTS", "true").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Use configuration
source = HTTPAPIDataSource(
    source_id="prod_api",
    api_url=Config.API_URL,
    api_key=Config.API_KEY
)
```

### Logging

Add comprehensive logging:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def production_pipeline():
    """Production pipeline with logging."""
    logger.info("Starting pipeline")
    
    source = HTTPAPIDataSource(...)
    storage = PostgreSQLStorageBackend(...)
    
    try:
        await source.connect()
        logger.info(f"Connected to source: {source.get_source_id()}")
        
        await storage.connect()
        logger.info(f"Connected to storage: {storage.get_backend_id()}")
        
        data = await source.collect()
        logger.info(f"Collected {len(data.raw_data)} bytes")
        
        location = await storage.store({"data": data.raw_data.decode()})
        logger.info(f"Stored at: {location.path}")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        raise
    finally:
        await source.disconnect()
        await storage.disconnect()
        logger.info("Pipeline completed")
```

### Monitoring

Use metrics and health checks:

```python
from prometheus_client import Counter, Histogram
import time

# Metrics
collection_counter = Counter('data_collections_total', 'Total data collections')
collection_errors = Counter('data_collection_errors_total', 'Collection errors')
collection_duration = Histogram('data_collection_duration_seconds', 'Collection duration')

async def monitored_pipeline():
    """Pipeline with monitoring."""
    source = HTTPAPIDataSource(...)
    storage = PostgreSQLStorageBackend(...)
    
    await source.connect()
    await storage.connect()
    
    try:
        start_time = time.time()
        
        data = await source.collect()
        collection_counter.inc()
        
        location = await storage.store({"data": data.raw_data.decode()})
        
        duration = time.time() - start_time
        collection_duration.observe(duration)
        
    except Exception as e:
        collection_errors.inc()
        raise
    finally:
        await source.disconnect()
        await storage.disconnect()
```

---

## Troubleshooting

### Common Issues

#### Issue: Connection Timeout

**Problem:** Data source connection times out

**Solution:**
```python
import asyncio

async def connect_with_timeout(source, timeout=30):
    """Connect with timeout."""
    try:
        await asyncio.wait_for(source.connect(), timeout=timeout)
    except asyncio.TimeoutError:
        raise ConnectionError(f"Connection timeout after {timeout}s")
```

#### Issue: Memory Leaks

**Problem:** Memory usage grows over time

**Solution:** Always disconnect and clean up resources:
```python
async def safe_pipeline():
    """Pipeline with guaranteed cleanup."""
    source = None
    storage = None
    
    try:
        source = HTTPAPIDataSource(...)
        storage = PostgreSQLStorageBackend(...)
        
        await source.connect()
        await storage.connect()
        
        # ... pipeline logic ...
        
    finally:
        if source:
            await source.disconnect()
        if storage:
            await storage.disconnect()
```

#### Issue: Processing Failures

**Problem:** Processing step fails intermittently

**Solution:** Add retry logic:
```python
async def process_with_retry(processor, data, max_retries=3):
    """Process with retry logic."""
    for attempt in range(max_retries):
        result = await processor.process(data)
        if result.success:
            return result
        
        if attempt < max_retries - 1:
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    raise RuntimeError(f"Processing failed after {max_retries} attempts")
```

### Debug Mode

Enable debug logging:

```python
import logging

logging.basicConfig(level=logging.DEBUG)

# Your pipeline code here
```

### Getting Help

- Check the API documentation: `API_DOCUMENTATION.md`
- Review usage examples: `examples.py`
- Check the design document: `.kiro/specs/data-collector-interfaces/design.md`

---

## Next Steps

1. Implement your custom components
2. Write unit tests for your implementations
3. Test with mock components first
4. Integrate with real data sources and storage
5. Add monitoring and logging
6. Deploy to production

For more examples, see `backend/src/collectors/examples.py`.
