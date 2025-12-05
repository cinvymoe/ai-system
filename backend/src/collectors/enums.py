"""Enumeration types for the Data Collector Module."""

from enum import Enum


class CollectionStatus(Enum):
    """采集状态"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class EventType(Enum):
    """事件类型"""
    COLLECTION_START = "collection_start"
    COLLECTION_COMPLETE = "collection_complete"
    PROCESSING_START = "processing_start"
    PROCESSING_COMPLETE = "processing_complete"
    STORAGE_START = "storage_start"
    STORAGE_COMPLETE = "storage_complete"
    ERROR_OCCURRED = "error_occurred"


class ErrorType(Enum):
    """错误类型"""
    CONFIGURATION = "configuration"
    CONNECTION = "connection"
    VALIDATION = "validation"
    PROCESSING = "processing"
    STORAGE = "storage"
