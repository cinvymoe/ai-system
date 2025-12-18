"""
Data Manager for Message Broker

负责统一管理和处理来自 broker 的消息订阅，实现优先级和去重逻辑。

功能：
1. 订阅 direction_result、angle_value、ai_alert 消息
2. 实现消息优先级：ai_alert > angle_value > direction_result
3. 消息持续时间管理（3秒）
4. 消息去重（相同类型 + 相同摄像头列表）
5. 高优先级消息可打断低优先级消息
"""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, field

try:
    from broker.broker import MessageBroker
    from broker.models import MessageData, CameraInfo
    from broker.handlers import PassthroughHandler
except ImportError:
    from src.broker.broker import MessageBroker
    from src.broker.models import MessageData, CameraInfo
    from src.broker.handlers import PassthroughHandler

logger = logging.getLogger(__name__)


@dataclass
class ManagedMessage:
    """管理的消息数据"""
    message_type: str  # 消息类型
    message_id: str  # 消息ID
    data: Dict[str, Any]  # 消息数据
    cameras: List[str]  # 摄像头ID列表（排序后）
    priority: int  # 优先级（数字越大优先级越高）
    timestamp: float  # 接收时间戳
    expire_time: float  # 过期时间戳
    
    def is_expired(self) -> bool:
        """检查消息是否已过期"""
        return time.time() >= self.expire_time
    
    def is_same_message(self, other: 'ManagedMessage') -> bool:
        """
        判断是否为相同消息
        
        相同消息的条件：
        1. 消息类型相同
        2. 摄像头列表相同（顺序无关）
        """
        return (
            self.message_type == other.message_type and
            self.cameras == other.cameras
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "message_type": self.message_type,
            "message_id": self.message_id,
            "data": self.data,
            "cameras": self.cameras,
            "priority": self.priority,
            "timestamp": self.timestamp,
            "expire_time": self.expire_time,
            "remaining_time": max(0, self.expire_time - time.time())
        }


class DataManager:
    """
    数据管理器
    
    统一管理来自 broker 的消息订阅，实现优先级和去重逻辑。
    """
    
    # 消息类型优先级定义（数字越大优先级越高）
    MESSAGE_PRIORITIES = {
        "ai_alert": 3,  # 最高优先级
        "angle_value": 2,  # 中等优先级
        "direction_result": 1  # 最低优先级
    }
    
    # 消息持续时间（秒）
    MESSAGE_DURATION = 3.0
    
    def __init__(
        self,
        camera_getter: Optional[Callable[[MessageData], List[CameraInfo]]] = None
    ):
        """
        初始化数据管理器
        
        Args:
            camera_getter: 获取摄像头列表的回调函数，接收 MessageData，返回 List[CameraInfo]
                          如果不提供，将使用空列表
        """
        self._broker: Optional[MessageBroker] = None
        self._camera_getter = camera_getter
        
        # 订阅ID列表
        self._subscription_ids: List[tuple] = []
        
        # 当前活跃的消息
        self._current_message: Optional[ManagedMessage] = None
        
        # 消息发送回调列表（用于通知外部）
        self._message_callbacks: List[Callable[[ManagedMessage], None]] = []
        
        # 定时器任务
        self._timer_task: Optional[asyncio.Task] = None
        
        # 锁（保护 _current_message）
        self._lock = asyncio.Lock()
        
        # 统计信息
        self._stats = {
            "messages_received": 0,
            "messages_sent": 0,
            "messages_interrupted": 0,
            "messages_duplicated": 0,
            "messages_expired": 0,
            "messages_no_cameras": 0
        }
        
        logger.info("DataManager initialized")
    
    def register_message_callback(
        self,
        callback: Callable[[ManagedMessage], None]
    ) -> None:
        """
        注册消息发送回调
        
        当有新消息需要发送时，会调用所有注册的回调函数。
        
        Args:
            callback: 回调函数，接收 ManagedMessage 参数
        """
        if callback not in self._message_callbacks:
            self._message_callbacks.append(callback)
            logger.info(f"Registered message callback: {callback.__name__}")
    
    def unregister_message_callback(
        self,
        callback: Callable[[ManagedMessage], None]
    ) -> None:
        """
        注销消息发送回调
        
        Args:
            callback: 要注销的回调函数
        """
        if callback in self._message_callbacks:
            self._message_callbacks.remove(callback)
            logger.info(f"Unregistered message callback: {callback.__name__}")
    
    async def initialize(self) -> None:
        """
        初始化数据管理器
        
        1. 获取 broker 实例
        2. 注册 data_manager 消息类型（使用 PassthroughHandler）
        3. 订阅 direction_result、angle_value、ai_alert 消息
        """
        try:
            # 获取 broker 实例
            self._broker = MessageBroker.get_instance()
            
            # 注册 data_manager 消息类型（使用 PassthroughHandler）
            if not self._broker.is_type_registered("data_manager"):
                handler = PassthroughHandler("data_manager")
                self._broker.register_message_type("data_manager", handler)
                logger.info("Registered data_manager message type with PassthroughHandler")
            
            # 订阅消息类型
            await self._subscribe_messages()
            
            logger.info("DataManager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize DataManager: {e}", exc_info=True)
            raise
    
    async def _subscribe_messages(self) -> None:
        """订阅所有需要的消息类型"""
        message_types = ["direction_result", "angle_value", "ai_alert"]
        
        for message_type in message_types:
            try:
                # 创建回调函数
                callback = self._create_message_callback(message_type)
                
                # 订阅消息
                sub_id = self._broker.subscribe(message_type, callback)
                self._subscription_ids.append((message_type, sub_id))
                
                logger.info(f"Subscribed to {message_type}: {sub_id}")
                
            except Exception as e:
                logger.error(f"Failed to subscribe to {message_type}: {e}", exc_info=True)
    
    def _create_message_callback(self, message_type: str) -> Callable:
        """
        创建消息回调函数
        
        Args:
            message_type: 消息类型
            
        Returns:
            Callable: 回调函数
        """
        def callback(message: MessageData):
            """消息回调（同步）"""
            # 将同步回调转换为异步任务
            try:
                loop = asyncio.get_running_loop()
                asyncio.create_task(self._handle_message(message))
            except RuntimeError:
                # No running event loop, create a new one
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self._handle_message(message))
        
        return callback
    
    async def _handle_message(self, message: MessageData) -> None:
        """
        处理接收到的消息
        
        实现逻辑：
        1. 获取消息对应的摄像头列表
        2. 创建 ManagedMessage
        3. 检查是否为重复消息
        4. 根据优先级决定是否发送/打断
        5. 启动定时器
        
        Args:
            message: 接收到的消息
        """
        async with self._lock:
            try:
                self._stats["messages_received"] += 1
                
                # 获取摄像头列表
                cameras = await self._get_cameras_for_message(message)
                camera_ids = sorted([cam.id for cam in cameras])
                
                # 获取优先级
                priority = self.MESSAGE_PRIORITIES.get(message.type, 0)
                
                # 创建 ManagedMessage
                current_time = time.time()
                managed_msg = ManagedMessage(
                    message_type=message.type,
                    message_id=message.message_id,
                    data=message.data,
                    cameras=camera_ids,
                    priority=priority,
                    timestamp=current_time,
                    expire_time=current_time + self.MESSAGE_DURATION
                )
                
                logger.debug(
                    f"Received message: type={message.type}, "
                    f"priority={priority}, cameras={len(camera_ids)}"
                )
                
                # 检查是否需要处理此消息
                should_send = await self._should_send_message(managed_msg)
                
                if should_send:
                    # 发送消息
                    await self._send_message(managed_msg)
                    
                    # 更新当前消息
                    self._current_message = managed_msg
                    
                    # 重启定时器
                    await self._restart_timer()
                else:
                    logger.debug(
                        f"Message not sent: type={message.type}, "
                        f"reason={'duplicate' if self._is_duplicate(managed_msg) else 'lower priority'}"
                    )
                
            except Exception as e:
                logger.error(f"Error handling message {message.message_id}: {e}", exc_info=True)
    
    async def _should_send_message(self, new_msg: ManagedMessage) -> bool:
        """
        判断是否应该发送新消息
        
        规则：
        0. 如果摄像头列表为空且消息不为ai_alert，不发送
        1. 如果没有当前消息，发送
        2. 如果当前消息已过期，发送
        3. 如果新消息与当前消息相同（去重），不发送
        4. 如果新消息优先级 >= 当前消息优先级，发送（打断）
        5. 否则不发送
        
        Args:
            new_msg: 新消息
            
        Returns:
            bool: 是否应该发送
        """
        # 检查摄像头列表是否为空且消息不为ai_alert
        if not new_msg.cameras and new_msg.message_type != "ai_alert":
            self._stats["messages_no_cameras"] += 1
            logger.debug(
                f"Message has no cameras and is not ai_alert, not sending: "
                f"type={new_msg.message_type}, id={new_msg.message_id}"
            )
            return False
        
        # 没有当前消息，直接发送
        if self._current_message is None:
            return True
        
        # 当前消息已过期，发送新消息
        if self._current_message.is_expired():
            self._stats["messages_expired"] += 1
            logger.debug("Current message expired, sending new message")
            return True
        
        # 检查是否为重复消息
        if self._is_duplicate(new_msg):
            self._stats["messages_duplicated"] += 1
            logger.debug("Duplicate message detected, not sending")
            return False
        
        # 比较优先级
        if new_msg.priority >= self._current_message.priority:
            # 高优先级或同优先级消息可以打断
            if new_msg.priority > self._current_message.priority:
                self._stats["messages_interrupted"] += 1
                logger.info(
                    f"Higher priority message interrupting: "
                    f"{new_msg.message_type}(p={new_msg.priority}) > "
                    f"{self._current_message.message_type}(p={self._current_message.priority})"
                )
            return True
        
        # 低优先级消息不发送
        logger.debug(
            f"Lower priority message ignored: "
            f"{new_msg.message_type}(p={new_msg.priority}) < "
            f"{self._current_message.message_type}(p={self._current_message.priority})"
        )
        return False
    
    def _is_duplicate(self, new_msg: ManagedMessage) -> bool:
        """
        检查是否为重复消息
        
        Args:
            new_msg: 新消息
            
        Returns:
            bool: 是否为重复消息
        """
        if self._current_message is None:
            return False
        
        return self._current_message.is_same_message(new_msg)
    
    async def _send_message(self, message: ManagedMessage) -> None:
        """
        发送消息到所有注册的回调
        
        Args:
            message: 要发送的消息
        """
        self._stats["messages_sent"] += 1
        
        logger.info(
            f"Sending message: type={message.message_type}, "
            f"cameras={len(message.cameras)}, priority={message.priority}"
        )
        
        # 调用所有注册的回调
        for callback in self._message_callbacks:
            try:
                # 检查回调是否为异步函数
                if asyncio.iscoroutinefunction(callback):
                    await callback(message)
                else:
                    callback(message)
            except Exception as e:
                logger.error(
                    f"Error in message callback {callback.__name__}: {e}",
                    exc_info=True
                )
    
    async def _restart_timer(self) -> None:
        """重启消息过期定时器"""
        # 取消现有定时器（如果存在）
        if self._timer_task:
            if not self._timer_task.done():
                self._timer_task.cancel()
            self._timer_task = None
        
        # 启动新定时器
        self._timer_task = asyncio.create_task(self._timer_expired())
    
    async def _timer_expired(self) -> None:
        """定时器到期处理"""
        try:
            # 等待消息持续时间
            await asyncio.sleep(self.MESSAGE_DURATION)
            
            async with self._lock:
                if self._current_message:
                    logger.debug(
                        f"Message expired: type={self._current_message.message_type}, "
                        f"id={self._current_message.message_id}"
                    )
                    self._current_message = None
                    self._stats["messages_expired"] += 1
                    
        except asyncio.CancelledError:
            logger.debug("Timer cancelled")
            # 重新抛出 CancelledError 以确保任务正确完成
            raise
        except Exception as e:
            logger.error(f"Error in timer: {e}", exc_info=True)
        finally:
            # 确保在任务完成时清理引用
            if self._timer_task and self._timer_task == asyncio.current_task():
                self._timer_task = None
    
    async def _get_cameras_for_message(self, message: MessageData) -> List[CameraInfo]:
        """
        获取消息对应的摄像头列表
        
        Args:
            message: 消息数据
            
        Returns:
            List[CameraInfo]: 摄像头列表
        """
        if self._camera_getter:
            try:
                result = self._camera_getter(message)
                # 如果返回的是协程，等待它
                if asyncio.iscoroutine(result):
                    return await result
                return result
            except Exception as e:
                logger.error(f"Error getting cameras for message: {e}", exc_info=True)
                return []
        
        return []
    
    async def shutdown(self) -> None:
        """关闭数据管理器，清理资源"""
        logger.info("Shutting down DataManager")
        
        async with self._lock:
            # 取消定时器
            if self._timer_task:
                if not self._timer_task.done():
                    self._timer_task.cancel()
                self._timer_task = None
            
            # 取消所有订阅
            if self._broker:
                for message_type, sub_id in self._subscription_ids:
                    try:
                        self._broker.unsubscribe(message_type, sub_id)
                        logger.info(f"Unsubscribed from {message_type}: {sub_id}")
                    except Exception as e:
                        logger.error(f"Error unsubscribing {sub_id}: {e}")
            
            self._subscription_ids.clear()
            self._current_message = None
            self._message_callbacks.clear()
        
        logger.info("DataManager shutdown complete")
    
    def get_current_message(self) -> Optional[Dict[str, Any]]:
        """
        获取当前活跃的消息
        
        Returns:
            Optional[Dict[str, Any]]: 当前消息的字典表示，如果没有则返回 None
        """
        if self._current_message and not self._current_message.is_expired():
            return self._current_message.to_dict()
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        return {
            **self._stats,
            "has_current_message": self._current_message is not None,
            "current_message": self.get_current_message()
        }
