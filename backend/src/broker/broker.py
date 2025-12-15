"""
Message Broker Core Implementation

全局消息代理（单例模式），负责消息的发布、订阅和分发。
"""

import logging
import threading
import time
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime

from .models import (
    MessageData,
    ProcessedMessage,
    PublishResult,
    SubscriptionInfo,
)
from .errors import (
    PublishError,
    SubscriptionError,
    MessageTypeError,
    ErrorHandler,
)

logger = logging.getLogger(__name__)


class MessageBroker:
    """
    全局消息代理（单例）
    
    负责管理消息类型、订阅者和消息分发。
    使用线程安全的单例模式确保全局唯一实例。
    """
    
    _instance: Optional['MessageBroker'] = None
    _lock: threading.Lock = threading.Lock()
    
    @classmethod
    def get_instance(cls) -> 'MessageBroker':
        """
        获取单例实例
        
        Returns:
            MessageBroker: 全局唯一的消息代理实例
        """
        if cls._instance is None:
            with cls._lock:
                # Double-check locking
                if cls._instance is None:
                    cls._instance = cls()
                    logger.info("MessageBroker singleton instance created")
        return cls._instance
    
    def __init__(self):
        """
        初始化消息代理
        
        注意：不应直接调用此方法，应使用 get_instance() 获取实例
        """
        if MessageBroker._instance is not None:
            raise RuntimeError(
                "MessageBroker is a singleton. Use get_instance() instead."
            )
        
        # 消息类型处理器注册表
        self._message_handlers: Dict[str, Any] = {}
        
        # 订阅者管理（message_type -> list of SubscriptionInfo）
        self._subscribers: Dict[str, List[SubscriptionInfo]] = {}
        
        # 线程安全锁
        self._subscription_lock = threading.RLock()
        self._handler_lock = threading.RLock()
        
        # 摄像头映射器（延迟初始化）
        self._camera_mapper: Optional[Any] = None
        
        # 错误处理器
        self._error_handler = ErrorHandler(logger)
        
        # 统计信息
        self._stats = {
            "messages_published": 0,
            "messages_failed": 0,
            "subscribers_count": 0,
        }
        
        logger.info("MessageBroker initialized")
    
    def register_message_type(
        self, 
        message_type: str, 
        handler: Any,
        allow_override: bool = False
    ) -> None:
        """
        注册新的消息类型处理器
        
        支持运行时动态注册新消息类型，实现可扩展架构。
        
        实现要求：
        - Requirements 6.1: 提供通用接口注册新消息类型
        - Requirements 6.2: 创建专用订阅通道
        - Requirements 6.3: 支持动态添加，无需修改核心代码
        - Requirements 6.4: 允许自定义验证规则（通过 handler）
        - Requirements 6.5: 确保向后兼容性
        
        Args:
            message_type: 消息类型名称
            handler: 消息类型处理器实例（实现 MessageTypeHandler 接口）
            allow_override: 是否允许覆盖已存在的处理器（默认 False）
            
        Raises:
            MessageTypeError: 如果消息类型已存在且 allow_override=False
        """
        with self._handler_lock:
            # 检查是否已注册
            if message_type in self._message_handlers:
                if not allow_override:
                    raise MessageTypeError(
                        f"Message type '{message_type}' is already registered. "
                        f"Use allow_override=True to replace the existing handler."
                    )
                logger.warning(
                    f"Overriding existing handler for message type: {message_type}"
                )
            
            # 验证 handler 实现了必需的接口
            if not hasattr(handler, 'validate') or not callable(handler.validate):
                raise MessageTypeError(
                    f"Handler for '{message_type}' must implement validate() method"
                )
            if not hasattr(handler, 'process') or not callable(handler.process):
                raise MessageTypeError(
                    f"Handler for '{message_type}' must implement process() method"
                )
            if not hasattr(handler, 'get_type_name') or not callable(handler.get_type_name):
                raise MessageTypeError(
                    f"Handler for '{message_type}' must implement get_type_name() method"
                )
            
            # 注册处理器
            self._message_handlers[message_type] = handler
            
            # 初始化该类型的订阅者列表（如果不存在）
            # 注意：如果是覆盖，保留现有订阅者（向后兼容）
            with self._subscription_lock:
                if message_type not in self._subscribers:
                    self._subscribers[message_type] = []
            
            logger.info(
                f"Registered message type: {message_type} "
                f"(handler: {handler.__class__.__name__})"
            )
    
    def set_camera_mapper(self, mapper: Any) -> None:
        """
        设置摄像头映射器
        
        Args:
            mapper: CameraMapper 实例
        """
        self._camera_mapper = mapper
        logger.info("Camera mapper set")
    
    def get_error_handler(self) -> ErrorHandler:
        """
        获取错误处理器
        
        Returns:
            ErrorHandler: 错误处理器实例
        """
        return self._error_handler
    
    def publish(
        self, 
        message_type: str, 
        data: Dict[str, Any]
    ) -> PublishResult:
        """
        发布消息
        
        Args:
            message_type: 消息类型
            data: 消息数据
            
        Returns:
            PublishResult: 发布结果
            
        Raises:
            PublishError: 如果发布失败
        """
        start_time = time.time()
        
        try:
            # 检查消息类型是否已注册
            if message_type not in self._message_handlers:
                raise PublishError(
                    f"Message type '{message_type}' is not registered"
                )
            
            # 创建消息对象
            message = MessageData(
                type=message_type,
                data=data,
                timestamp=datetime.now()
            )
            
            # 验证消息
            handler = self._message_handlers[message_type]
            validation_result = handler.validate(data)
            
            if not validation_result.valid:
                self._stats["messages_failed"] += 1
                # 使用 ErrorHandler 处理验证错误
                self._error_handler.handle_validation_error(message, validation_result)
                return PublishResult(
                    success=False,
                    message_id=message.message_id,
                    subscribers_notified=0,
                    errors=validation_result.errors
                )
            
            # 处理消息
            processed = handler.process(data)
            
            # 通知订阅者
            notified_count = self._notify_subscribers(message_type, message)
            
            self._stats["messages_published"] += 1
            
            processing_time = time.time() - start_time
            
            logger.info(
                f"Published message {message.message_id} of type {message_type}, "
                f"notified {notified_count} subscribers in {processing_time:.4f}s"
            )
            
            return PublishResult(
                success=True,
                message_id=message.message_id,
                subscribers_notified=notified_count,
                errors=[]
            )
            
        except Exception as e:
            self._stats["messages_failed"] += 1
            logger.error(f"Failed to publish message: {e}", exc_info=True)
            raise PublishError(f"Failed to publish message: {e}")
    
    def subscribe(
        self, 
        message_type: str, 
        callback: Callable[[MessageData], None]
    ) -> str:
        """
        订阅消息类型
        
        实现要求：
        - 注册订阅者回调 (Requirements 4.1, 5.1)
        - 线程安全的订阅注册 (Requirement 9.2)
        
        Args:
            message_type: 消息类型
            callback: 回调函数，接收 MessageData 参数
            
        Returns:
            str: 订阅ID
            
        Raises:
            SubscriptionError: 如果订阅失败
        """
        if not callable(callback):
            raise SubscriptionError("Callback must be callable")
        
        with self._subscription_lock:
            # 检查消息类型是否已注册
            if message_type not in self._message_handlers:
                raise SubscriptionError(
                    f"Message type '{message_type}' is not registered. "
                    f"Available types: {list(self._message_handlers.keys())}"
                )
            
            # 创建订阅信息
            subscription = SubscriptionInfo(
                subscription_id=f"sub_{message_type}_{id(callback)}_{time.time()}",
                message_type=message_type,
                callback=callback
            )
            
            # 添加到订阅者列表
            if message_type not in self._subscribers:
                self._subscribers[message_type] = []
            
            self._subscribers[message_type].append(subscription)
            self._stats["subscribers_count"] += 1
            
            logger.info(
                f"Subscriber {subscription.subscription_id} registered "
                f"for message type '{message_type}' "
                f"(total subscribers for this type: {len(self._subscribers[message_type])})"
            )
            
            return subscription.subscription_id
    
    def unsubscribe(
        self, 
        message_type: str, 
        subscription_id: str
    ) -> bool:
        """
        取消订阅
        
        实现要求：
        - 线程安全的取消订阅 (Requirement 9.2)
        
        Args:
            message_type: 消息类型
            subscription_id: 订阅ID
            
        Returns:
            bool: 是否成功取消订阅
        """
        with self._subscription_lock:
            if message_type not in self._subscribers:
                logger.warning(
                    f"Cannot unsubscribe {subscription_id}: "
                    f"message type '{message_type}' not found"
                )
                return False
            
            # 查找并移除订阅
            subscribers = self._subscribers[message_type]
            for i, sub in enumerate(subscribers):
                if sub.subscription_id == subscription_id:
                    subscribers.pop(i)
                    self._stats["subscribers_count"] -= 1
                    logger.info(
                        f"Unsubscribed {subscription_id} from '{message_type}' "
                        f"(remaining subscribers for this type: {len(subscribers)})"
                    )
                    return True
            
            logger.warning(
                f"Cannot unsubscribe {subscription_id}: subscription not found"
            )
            return False
    
    def _notify_subscribers(
        self, 
        message_type: str, 
        message: MessageData
    ) -> int:
        """
        通知所有订阅者
        
        实现要求：
        - 通知所有注册的订阅者 (Requirements 2.3, 3.3)
        - 订阅者错误隔离，不影响其他订阅者 (Requirement 9.5)
        - 线程安全 (Requirements 9.1, 9.2)
        - 保持消息顺序 (Requirement 2.5)
        
        Args:
            message_type: 消息类型
            message: 消息数据
            
        Returns:
            int: 成功通知的订阅者数量
        """
        # 获取订阅者列表的快照（线程安全）
        with self._subscription_lock:
            if message_type not in self._subscribers:
                logger.debug(f"No subscribers for message type: {message_type}")
                return 0
            
            # 创建订阅者列表的副本，避免在通知过程中列表被修改
            subscribers = self._subscribers[message_type].copy()
        
        if not subscribers:
            logger.debug(f"Empty subscriber list for message type: {message_type}")
            return 0
        
        notified_count = 0
        failed_count = 0
        
        # 按顺序通知每个订阅者
        for subscription in subscribers:
            try:
                # 调用订阅者回调
                subscription.callback(message)
                notified_count += 1
                logger.debug(
                    f"Notified subscriber {subscription.subscription_id} "
                    f"for message {message.message_id}"
                )
            except Exception as e:
                # 订阅者错误不应影响其他订阅者 (Requirement 9.5)
                failed_count += 1
                # 使用 ErrorHandler 处理订阅者错误
                self._error_handler.handle_subscriber_error(
                    subscription.subscription_id,
                    e,
                    message.message_id
                )
        
        if failed_count > 0:
            logger.warning(
                f"Message {message.message_id}: {notified_count} subscribers notified, "
                f"{failed_count} failed"
            )
        
        return notified_count
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        return self._stats.copy()
    
    def is_type_registered(self, message_type: str) -> bool:
        """
        检查消息类型是否已注册
        
        Args:
            message_type: 消息类型名称
            
        Returns:
            bool: 如果已注册返回 True，否则返回 False
        """
        with self._handler_lock:
            return message_type in self._message_handlers
    
    def unregister_message_type(self, message_type: str) -> bool:
        """
        注销消息类型处理器
        
        注意：注销后，该类型的现有订阅者将无法接收新消息，
        但订阅者列表会被保留以保持向后兼容性。
        
        Args:
            message_type: 消息类型名称
            
        Returns:
            bool: 如果成功注销返回 True，如果类型不存在返回 False
        """
        with self._handler_lock:
            if message_type not in self._message_handlers:
                logger.warning(
                    f"Cannot unregister message type '{message_type}': not registered"
                )
                return False
            
            del self._message_handlers[message_type]
            logger.info(f"Unregistered message type: {message_type}")
            
            # 注意：不删除订阅者列表，保持向后兼容性
            # 如果类型被重新注册，订阅者仍然有效
            
            return True
    
    def get_registered_types(self) -> List[str]:
        """
        获取已注册的消息类型列表
        
        Returns:
            List[str]: 消息类型列表
        """
        with self._handler_lock:
            return list(self._message_handlers.keys())
    
    def get_handler(self, message_type: str) -> Optional[Any]:
        """
        获取指定消息类型的处理器
        
        Args:
            message_type: 消息类型名称
            
        Returns:
            Optional[Any]: 处理器实例，如果不存在返回 None
        """
        with self._handler_lock:
            return self._message_handlers.get(message_type)
    
    def get_subscriber_count(self, message_type: Optional[str] = None) -> int:
        """
        获取订阅者数量
        
        Args:
            message_type: 消息类型（可选），如果不指定则返回总数
            
        Returns:
            int: 订阅者数量
        """
        with self._subscription_lock:
            if message_type:
                return len(self._subscribers.get(message_type, []))
            else:
                return sum(len(subs) for subs in self._subscribers.values())
    
    def get_subscribers(self, message_type: str) -> List[Dict[str, Any]]:
        """
        获取指定消息类型的所有订阅者信息（不包含回调函数）
        
        Args:
            message_type: 消息类型
            
        Returns:
            List[Dict[str, Any]]: 订阅者信息列表
        """
        with self._subscription_lock:
            if message_type not in self._subscribers:
                return []
            
            return [sub.to_dict() for sub in self._subscribers[message_type]]
    
    def initialize_handlers(
        self,
        camera_mapper: Any,
        handlers: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        初始化消息代理的处理器和映射器
        
        这个方法将初始化逻辑从API层解耦到MessageBroker内部，
        使得MessageBroker可以独立完成初始化。
        
        Args:
            camera_mapper: CameraMapper实例，用于摄像头映射
            handlers: 可选的消息类型处理器字典 {message_type: handler}
                     如果不提供，将使用默认处理器
        """
        # 设置摄像头映射器
        self.set_camera_mapper(camera_mapper)
        
        # 如果提供了自定义处理器，使用它们
        if handlers:
            for message_type, handler in handlers.items():
                self.register_message_type(message_type, handler)
            logger.info(f"Registered {len(handlers)} custom message handlers")
        else:
            # 使用默认处理器
            try:
                from .handlers import (
                    DirectionMessageHandler,
                    AngleMessageHandler,
                    AIAlertMessageHandler,
                )
            except ImportError:
                from src.broker.handlers import (
                    DirectionMessageHandler,
                    AngleMessageHandler,
                    AIAlertMessageHandler,
                )
            
            # 注册默认消息类型处理器
            self.register_message_type("direction_result", DirectionMessageHandler())
            self.register_message_type("angle_value", AngleMessageHandler())
            self.register_message_type("ai_alert", AIAlertMessageHandler())            
            logger.info("Registered default message handlers (direction_result, angle_value, ai_alert)")
    
    def shutdown(self) -> None:
        """关闭消息代理，清理资源"""
        logger.info("Shutting down MessageBroker")
        with self._subscription_lock:
            self._subscribers.clear()
        with self._handler_lock:
            self._message_handlers.clear()
        self._stats["subscribers_count"] = 0
        logger.info("MessageBroker shutdown complete")
