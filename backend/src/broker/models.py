"""
Data models for the Message Broker module.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid


@dataclass
class MessageData:
    """消息数据"""
    type: str  # 消息类型: direction_result, angle_value, ai_alert
    data: Dict[str, Any]  # 消息内容
    timestamp: datetime
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))  # 唯一消息ID

    def __post_init__(self):
        """确保 timestamp 是 datetime 对象"""
        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp)


@dataclass
class CameraInfo:
    """摄像头信息"""
    id: str
    name: str
    url: str
    status: str  # online/offline
    directions: List[str] = field(default_factory=list)  # 关联的方向
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "status": self.status,
            "directions": self.directions,
        }


@dataclass
class ProcessedMessage:
    """处理后的消息"""
    original: MessageData
    validated: bool
    cameras: List[CameraInfo]
    processing_time: float
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "message_id": self.original.message_id,
            "type": self.original.type,
            "validated": self.validated,
            "cameras": [cam.to_dict() for cam in self.cameras],
            "processing_time": self.processing_time,
            "errors": self.errors,
            "timestamp": self.original.timestamp.isoformat(),
        }


@dataclass
class PublishResult:
    """发布结果"""
    success: bool
    message_id: str
    subscribers_notified: int
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "success": self.success,
            "message_id": self.message_id,
            "subscribers_notified": self.subscribers_notified,
            "errors": self.errors,
        }


@dataclass
class ValidationResult:
    """验证结果"""
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "valid": self.valid,
            "errors": self.errors,
            "warnings": self.warnings,
        }


@dataclass
class SubscriptionInfo:
    """订阅信息"""
    subscription_id: str
    message_type: str
    callback: Any  # Callable
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（不包含 callback）"""
        return {
            "subscription_id": self.subscription_id,
            "message_type": self.message_type,
            "created_at": self.created_at.isoformat(),
        }
