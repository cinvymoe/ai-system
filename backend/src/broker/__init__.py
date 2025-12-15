"""
Message Broker Module

全局消息代理模块，负责订阅传感器数据（方向处理结果和角度值），
并将这些数据映射到对应的摄像头地址列表。

支持发布-订阅模式，提供可扩展的架构以支持未来添加新的消息类型。
"""

from .broker import MessageBroker
from .models import (
    MessageData,
    ProcessedMessage,
    CameraInfo,
    PublishResult,
    ValidationResult,
)
from .handlers import (
    MessageTypeHandler,
    DirectionMessageHandler,
    AngleMessageHandler,
    AIAlertMessageHandler,
    PassthroughHandler,
)
from .mapper import CameraMapper
from .errors import (
    BrokerError,
    ValidationError,
    SubscriptionError,
    PublishError,
    ErrorHandler,
)
from .logging_config import (
    configure_broker_logging,
    get_broker_logger,
    BrokerLoggerAdapter,
    create_message_logger,
    create_subscriber_logger,
    setup_default_logging,
)

__all__ = [
    "MessageBroker",
    "MessageData",
    "ProcessedMessage",
    "CameraInfo",
    "PublishResult",
    "ValidationResult",
    "MessageTypeHandler",
    "DirectionMessageHandler",
    "AngleMessageHandler",
    "AIAlertMessageHandler",
    "PassthroughHandler",
    "CameraMapper",
    "BrokerError",
    "ValidationError",
    "SubscriptionError",
    "PublishError",
    "ErrorHandler",
    "configure_broker_logging",
    "get_broker_logger",
    "BrokerLoggerAdapter",
    "create_message_logger",
    "create_subscriber_logger",
    "setup_default_logging",
]
