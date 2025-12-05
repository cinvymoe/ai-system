"""Tests for mock implementations."""

import pytest
from datetime import datetime

from src.collectors import (
    MockDataSource,
    MockMetadataParser,
    MockProcessor,
    MockStorageBackend,
    MockErrorHandler,
    MockEventEmitter,
    MockTaskTracker,
    ErrorType,
    EventType,
    TaskStatus,
    ErrorInfo,
    SystemEvent,
    QueryCriteria,
)


class TestMockDataSource:
    """Test MockDataSource implementation."""
    
    @pytest.mark.asyncio
    async def test_connect_disconnect(self):
        """Test connection lifecycle."""
        source = MockDataSource("test_source")
        assert not source.is_connected()
        
        await source.connect()
        assert source.is_connected()
        
        await source.disconnect()
        assert not source.is_connected()
    
    @pytest.mark.asyncio
    async def test_collect(self):
        """Test data collection."""
        source = MockDataSource("test_source", b"test_data")
        await source.connect()
        
        data = await source.collect()
        assert data.source_id == "test_source"
        assert data.raw_data == b"test_data"
        assert data.data_format == "mock"
        assert source.get_collect_count() == 1
    
    @pytest.mark.asyncio
    async def test_collect_stream(self):
        """Test stream collection."""
        source = MockDataSource("test_source")
        await source.connect()
        
        collected = []
        async for data in source.collect_stream():
            collected.append(data)
        
        assert len(collected) == 3
        assert all(d.source_id == "test_source" for d in collected)


class TestMockMetadataParser:
    """Test MockMetadataParser implementation."""
    
    @pytest.mark.asyncio
    async def test_parse_valid(self):
        """Test parsing with valid result."""
        parser = MockMetadataParser(validation_result=True)
        source = MockDataSource("test_source")
        await source.connect()
        data = await source.collect()
        
        metadata = await parser.parse(data)
        assert metadata.is_valid
        assert len(metadata.validation_errors) == 0
        assert parser.get_parse_count() == 1
    
    @pytest.mark.asyncio
    async def test_parse_invalid(self):
        """Test parsing with invalid result."""
        parser = MockMetadataParser(validation_result=False)
        source = MockDataSource("test_source")
        await source.connect()
        data = await source.collect()
        
        metadata = await parser.parse(data)
        assert not metadata.is_valid
        assert len(metadata.validation_errors) > 0


class TestMockProcessor:
    """Test MockProcessor implementation."""
    
    @pytest.mark.asyncio
    async def test_process_success(self):
        """Test successful processing."""
        processor = MockProcessor("test_processor")
        data = {"key": "value"}
        
        result = await processor.process(data)
        assert result.success
        assert result.processed_data is not None
        assert "processed_by_test_processor" in result.processed_data
        assert processor.get_process_count() == 1
    
    @pytest.mark.asyncio
    async def test_process_failure(self):
        """Test processing failure."""
        processor = MockProcessor("test_processor", should_fail=True)
        data = {"key": "value"}
        
        result = await processor.process(data)
        assert not result.success
        assert result.error is not None
        assert "failed" in result.error


class TestMockStorageBackend:
    """Test MockStorageBackend implementation."""
    
    @pytest.mark.asyncio
    async def test_store_and_query(self):
        """Test storing and querying data."""
        backend = MockStorageBackend("test_backend")
        await backend.connect()
        
        # Store data
        data = {"key": "value"}
        location = await backend.store(data)
        assert location.backend_id == "test_backend"
        assert location.location_id is not None
        assert backend.get_store_count() == 1
        
        # Query data
        criteria = QueryCriteria(filters={}, sort_by=None, limit=None, offset=None)
        results = await backend.query(criteria)
        assert len(results) == 1
        assert results[0] == data
    
    @pytest.mark.asyncio
    async def test_delete(self):
        """Test deleting data."""
        backend = MockStorageBackend("test_backend")
        await backend.connect()
        
        # Store and delete
        location = await backend.store({"key": "value"})
        await backend.delete(location.location_id)
        
        # Verify deletion
        criteria = QueryCriteria(filters={}, sort_by=None, limit=None, offset=None)
        results = await backend.query(criteria)
        assert len(results) == 0


class TestMockErrorHandler:
    """Test MockErrorHandler implementation."""
    
    @pytest.mark.asyncio
    async def test_handle_error(self):
        """Test error handling."""
        handler = MockErrorHandler()
        error = ErrorInfo(
            error_type=ErrorType.VALIDATION,
            timestamp=datetime.now(),
            layer_name="test_layer",
            operation="test_op",
            message="Test error",
            details={},
            is_critical=False
        )
        
        await handler.handle_error(error)
        assert handler.get_error_count() == 1
        errors = handler.get_handled_errors()
        assert errors[0].message == "Test error"
    
    def test_can_handle(self):
        """Test error type filtering."""
        handler = MockErrorHandler(handled_types=[ErrorType.VALIDATION])
        assert handler.can_handle(ErrorType.VALIDATION)
        assert not handler.can_handle(ErrorType.CONNECTION)


class TestMockEventEmitter:
    """Test MockEventEmitter implementation."""
    
    @pytest.mark.asyncio
    async def test_emit_and_subscribe(self):
        """Test event emission and subscription."""
        emitter = MockEventEmitter()
        received_events = []
        
        def handler(event):
            received_events.append(event)
        
        # Subscribe
        sub_id = await emitter.subscribe(EventType.COLLECTION_START, handler)
        assert emitter.get_subscription_count() == 1
        
        # Emit event
        event = SystemEvent(
            event_type=EventType.COLLECTION_START,
            timestamp=datetime.now(),
            source="test",
            data={}
        )
        await emitter.emit(event)
        
        assert emitter.get_event_count() == 1
        assert len(received_events) == 1
        
        # Unsubscribe
        await emitter.unsubscribe(sub_id)
        assert emitter.get_subscription_count() == 0


class TestMockTaskTracker:
    """Test MockTaskTracker implementation."""
    
    @pytest.mark.asyncio
    async def test_create_and_update_task(self):
        """Test task creation and updates."""
        tracker = MockTaskTracker()
        
        # Create task
        task_id = await tracker.create_task("test_task")
        assert tracker.get_task_count() == 1
        
        # Update status
        await tracker.update_status(task_id, TaskStatus.RUNNING)
        task_info = await tracker.get_task_info(task_id)
        assert task_info.status == TaskStatus.RUNNING
        assert task_info.started_at is not None
        
        # Update progress
        await tracker.update_progress(task_id, 0.5)
        task_info = await tracker.get_task_info(task_id)
        assert task_info.progress == 0.5
    
    @pytest.mark.asyncio
    async def test_cancel_task(self):
        """Test task cancellation."""
        tracker = MockTaskTracker()
        task_id = await tracker.create_task("test_task")
        
        await tracker.cancel_task(task_id)
        task_info = await tracker.get_task_info(task_id)
        assert task_info.status == TaskStatus.CANCELLED
