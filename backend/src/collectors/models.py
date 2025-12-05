"""Data models for the Data Collector Module."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

from .enums import CollectionStatus, TaskStatus, EventType, ErrorType


@dataclass
class CollectedData:
    """采集到的原始数据及其元数据"""
    source_id: str
    timestamp: datetime
    data_format: str
    collection_method: str
    raw_data: bytes
    metadata: Dict[str, Any]


@dataclass
class ParsedMetadata:
    """解析后的元数据"""
    schema: Dict[str, Any]
    quality_indicators: Dict[str, float]
    source_attributes: Dict[str, Any]
    is_valid: bool
    validation_errors: list[str]


@dataclass
class CollectionTask:
    """采集任务"""
    task_id: str
    source_id: str
    status: CollectionStatus
    created_at: datetime
    started_at: Optional[datetime]
    stopped_at: Optional[datetime]


@dataclass
class CollectionStatistics:
    """采集统计信息"""
    success_count: int
    failure_count: int
    average_processing_time: float
    last_collection_time: Optional[datetime]


@dataclass
class ProcessingResult:
    """处理结果"""
    success: bool
    processed_data: Optional[Any]
    error: Optional[str]
    processing_time: float


@dataclass
class PipelineStep:
    """管道步骤"""
    step_id: str
    processor: Any  # IProcessor interface will be defined later
    order: int


@dataclass
class PipelineResult:
    """管道执行结果"""
    success: bool
    final_data: Optional[Any]
    step_results: list[ProcessingResult]
    failed_step: Optional[str]
    total_time: float


@dataclass
class ProcessingStatistics:
    """处理统计信息"""
    step_name: str
    execution_count: int
    success_count: int
    failure_count: int
    average_time: float


@dataclass
class StorageLocation:
    """存储位置"""
    backend_id: str
    location_id: str
    path: str
    created_at: datetime


@dataclass
class QueryCriteria:
    """查询条件"""
    filters: Dict[str, Any]
    sort_by: Optional[str]
    limit: Optional[int]
    offset: Optional[int]


@dataclass
class StorageStatistics:
    """存储统计信息"""
    backend_id: str
    stored_count: int
    storage_usage_bytes: int
    last_storage_time: Optional[datetime]


@dataclass
class ErrorInfo:
    """错误信息"""
    error_type: ErrorType
    timestamp: datetime
    layer_name: str
    operation: str
    message: str
    details: Dict[str, Any]
    is_critical: bool


@dataclass
class SystemEvent:
    """系统事件"""
    event_type: EventType
    timestamp: datetime
    source: str
    data: Dict[str, Any]


@dataclass
class TaskInfo:
    """任务信息"""
    task_id: str
    task_type: str
    status: TaskStatus
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    progress: float
    result: Optional[Any]
    error: Optional[str]


@dataclass
class MotionCommand:
    """运动指令"""
    command: str  # 'forward', 'backward', 'turn_left', 'turn_right', 'stationary'
    intensity: float  # 运动强度
    angular_intensity: float  # 旋转强度
    timestamp: datetime
    is_motion_start: bool  # 是否是运动开始
    raw_direction: str  # 原始方向字符串
    metadata: Dict[str, Any]
