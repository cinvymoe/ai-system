"""
MessageBroker 核心功能测试

测试消息代理的单例模式、消息类型注册、发布订阅机制等核心功能。
"""

import pytest
import threading
import time
from datetime import datetime
from typing import List

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.broker.broker import MessageBroker
from src.broker.models import MessageData, ValidationResult, ProcessedMessage
from src.broker.errors import (
    PublishError,
    SubscriptionError,
    MessageTypeError,
)
from src.broker.handlers import (
    MessageTypeHandler,
    DirectionMessageHandler,
    AngleMessageHandler,
    AIAlertMessageHandler,
)


class MockMessageHandler(MessageTypeHandler):
    """模拟消息处理器，用于测试"""
    
    def __init__(self, type_name: str = "mock_type"):
        self.type_name = type_name
        self.validate_called = False
        self.process_called = False
    
    def validate(self, data: dict) -> ValidationResult:
        self.validate_called = True
        # 简单验证：检查是否有 'value' 字段
        if 'value' not in data:
            return ValidationResult(
                valid=False,
                errors=["Missing 'value' field"]
            )
        return ValidationResult(valid=True)
    
    def process(self, data: dict) -> ProcessedMessage:
        self.process_called = True
        message = MessageData(
            type=self.type_name,
            data=data,
            timestamp=datetime.now()
        )
        return ProcessedMessage(
            original=message,
            validated=True,
            cameras=[],
            processing_time=0.0
        )
    
    def get_type_name(self) -> str:
        return self.type_name


@pytest.fixture
def broker():
    """创建新的 MessageBroker 实例用于测试"""
    # 重置单例
    MessageBroker._instance = None
    broker = MessageBroker.get_instance()
    yield broker
    # 清理
    broker.shutdown()
    MessageBroker._instance = None


class TestBrokerSingleton:
    """测试单例模式"""
    
    def test_singleton_same_instance(self):
        """测试多次调用 get_instance() 返回同一实例"""
        MessageBroker._instance = None
        broker1 = MessageBroker.get_instance()
        broker2 = MessageBroker.get_instance()
        assert broker1 is broker2
        broker1.shutdown()
        MessageBroker._instance = None
    
    def test_singleton_thread_safe(self):
        """测试单例在多线程环境下的安全性"""
        MessageBroker._instance = None
        instances = []
        
        def get_broker():
            instances.append(MessageBroker.get_instance())
        
        threads = [threading.Thread(target=get_broker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # 所有实例应该相同
        assert all(inst is instances[0] for inst in instances)
        instances[0].shutdown()
        MessageBroker._instance = None
    
    def test_direct_init_raises_error(self):
        """测试直接调用 __init__ 会抛出错误"""
        MessageBroker._instance = MessageBroker.get_instance()
        with pytest.raises(RuntimeError, match="singleton"):
            MessageBroker()
        MessageBroker._instance.shutdown()
        MessageBroker._instance = None


class TestMessageTypeRegistration:
    """测试消息类型注册"""
    
    def test_register_message_type(self, broker):
        """测试注册新消息类型"""
        handler = MockMessageHandler("test_type")
        broker.register_message_type("test_type", handler)
        
        assert broker.is_type_registered("test_type")
        assert "test_type" in broker.get_registered_types()
    
    def test_register_duplicate_type_fails(self, broker):
        """测试重复注册相同类型会失败"""
        handler1 = MockMessageHandler("test_type")
        handler2 = MockMessageHandler("test_type")
        
        broker.register_message_type("test_type", handler1)
        
        with pytest.raises(MessageTypeError, match="already registered"):
            broker.register_message_type("test_type", handler2)
    
    def test_register_duplicate_with_override(self, broker):
        """测试使用 allow_override 可以覆盖已注册的类型"""
        handler1 = MockMessageHandler("test_type")
        handler2 = MockMessageHandler("test_type")
        
        broker.register_message_type("test_type", handler1)
        broker.register_message_type("test_type", handler2, allow_override=True)
        
        # 应该使用新的处理器
        retrieved_handler = broker.get_handler("test_type")
        assert retrieved_handler is handler2
    
    def test_register_invalid_handler_fails(self, broker):
        """测试注册无效的处理器会失败"""
        class InvalidHandler:
            pass
        
        with pytest.raises(MessageTypeError, match="must implement validate"):
            broker.register_message_type("invalid", InvalidHandler())
    
    def test_unregister_message_type(self, broker):
        """测试注销消息类型"""
        handler = MockMessageHandler("test_type")
        broker.register_message_type("test_type", handler)
        
        assert broker.is_type_registered("test_type")
        
        result = broker.unregister_message_type("test_type")
        assert result is True
        assert not broker.is_type_registered("test_type")
    
    def test_unregister_nonexistent_type(self, broker):
        """测试注销不存在的类型返回 False"""
        result = broker.unregister_message_type("nonexistent")
        assert result is False


class TestPublishSubscribe:
    """测试发布订阅机制"""
    
    def test_subscribe_to_message_type(self, broker):
        """测试订阅消息类型"""
        handler = MockMessageHandler("test_type")
        broker.register_message_type("test_type", handler)
        
        received_messages = []
        
        def callback(message: MessageData):
            received_messages.append(message)
        
        sub_id = broker.subscribe("test_type", callback)
        assert sub_id is not None
        assert broker.get_subscriber_count("test_type") == 1
    
    def test_subscribe_to_unregistered_type_fails(self, broker):
        """测试订阅未注册的类型会失败"""
        def callback(message: MessageData):
            pass
        
        with pytest.raises(SubscriptionError, match="not registered"):
            broker.subscribe("nonexistent_type", callback)
    
    def test_subscribe_with_invalid_callback_fails(self, broker):
        """测试使用无效回调订阅会失败"""
        handler = MockMessageHandler("test_type")
        broker.register_message_type("test_type", handler)
        
        with pytest.raises(SubscriptionError, match="must be callable"):
            broker.subscribe("test_type", "not_a_function")
    
    def test_publish_message(self, broker):
        """测试发布消息"""
        handler = MockMessageHandler("test_type")
        broker.register_message_type("test_type", handler)
        
        received_messages = []
        
        def callback(message: MessageData):
            received_messages.append(message)
        
        broker.subscribe("test_type", callback)
        
        result = broker.publish("test_type", {"value": "test"})
        
        assert result.success is True
        assert result.subscribers_notified == 1
        assert len(received_messages) == 1
        assert received_messages[0].data["value"] == "test"
    
    def test_publish_to_unregistered_type_fails(self, broker):
        """测试发布到未注册的类型会失败"""
        with pytest.raises(PublishError, match="not registered"):
            broker.publish("nonexistent_type", {"value": "test"})
    
    def test_publish_invalid_message_fails(self, broker):
        """测试发布无效消息会失败验证"""
        handler = MockMessageHandler("test_type")
        broker.register_message_type("test_type", handler)
        
        # 缺少 'value' 字段
        result = broker.publish("test_type", {})
        
        assert result.success is False
        assert len(result.errors) > 0
    
    def test_multiple_subscribers(self, broker):
        """测试多个订阅者"""
        handler = MockMessageHandler("test_type")
        broker.register_message_type("test_type", handler)
        
        received_by_sub1 = []
        received_by_sub2 = []
        received_by_sub3 = []
        
        def callback1(msg):
            received_by_sub1.append(msg)
        
        def callback2(msg):
            received_by_sub2.append(msg)
        
        def callback3(msg):
            received_by_sub3.append(msg)
        
        broker.subscribe("test_type", callback1)
        broker.subscribe("test_type", callback2)
        broker.subscribe("test_type", callback3)
        
        result = broker.publish("test_type", {"value": "broadcast"})
        
        assert result.success is True
        assert result.subscribers_notified == 3
        assert len(received_by_sub1) == 1
        assert len(received_by_sub2) == 1
        assert len(received_by_sub3) == 1
    
    def test_unsubscribe(self, broker):
        """测试取消订阅"""
        handler = MockMessageHandler("test_type")
        broker.register_message_type("test_type", handler)
        
        received_messages = []
        
        def callback(message: MessageData):
            received_messages.append(message)
        
        sub_id = broker.subscribe("test_type", callback)
        
        # 发布第一条消息
        broker.publish("test_type", {"value": "first"})
        assert len(received_messages) == 1
        
        # 取消订阅
        result = broker.unsubscribe("test_type", sub_id)
        assert result is True
        
        # 发布第二条消息
        broker.publish("test_type", {"value": "second"})
        # 不应该收到第二条消息
        assert len(received_messages) == 1
    
    def test_subscriber_error_isolation(self, broker):
        """测试订阅者错误隔离 - 一个订阅者失败不影响其他订阅者"""
        handler = MockMessageHandler("test_type")
        broker.register_message_type("test_type", handler)
        
        received_by_good_sub = []
        
        def failing_callback(msg):
            raise Exception("Subscriber error!")
        
        def good_callback(msg):
            received_by_good_sub.append(msg)
        
        broker.subscribe("test_type", failing_callback)
        broker.subscribe("test_type", good_callback)
        
        result = broker.publish("test_type", {"value": "test"})
        
        # 发布应该成功，但只有一个订阅者收到消息
        assert result.success is True
        assert result.subscribers_notified == 1
        assert len(received_by_good_sub) == 1


class TestBuiltInHandlers:
    """测试内置消息处理器"""
    
    def test_direction_handler(self, broker):
        """测试方向消息处理器"""
        handler = DirectionMessageHandler()
        broker.register_message_type("direction_result", handler)
        
        received_messages = []
        broker.subscribe("direction_result", lambda msg: received_messages.append(msg))
        
        # 有效的方向消息
        result = broker.publish("direction_result", {
            "command": "forward",
            "timestamp": datetime.now().isoformat()
        })
        
        assert result.success is True
        assert len(received_messages) == 1
    
    def test_direction_handler_invalid_command(self, broker):
        """测试方向处理器拒绝无效命令"""
        handler = DirectionMessageHandler()
        broker.register_message_type("direction_result", handler)
        
        result = broker.publish("direction_result", {
            "command": "invalid_command"
        })
        
        assert result.success is False
        assert any("Invalid command" in err for err in result.errors)
    
    def test_angle_handler(self, broker):
        """测试角度消息处理器"""
        handler = AngleMessageHandler()
        broker.register_message_type("angle_value", handler)
        
        received_messages = []
        broker.subscribe("angle_value", lambda msg: received_messages.append(msg))
        
        # 有效的角度消息
        result = broker.publish("angle_value", {
            "angle": 45.5,
            "timestamp": datetime.now().isoformat()
        })
        
        assert result.success is True
        assert len(received_messages) == 1
    
    def test_angle_handler_out_of_range(self, broker):
        """测试角度处理器拒绝超出范围的角度"""
        handler = AngleMessageHandler()
        broker.register_message_type("angle_value", handler)
        
        result = broker.publish("angle_value", {
            "angle": 500.0  # 超出范围
        })
        
        assert result.success is False
        assert any("out of valid range" in err for err in result.errors)
    
    def test_ai_alert_handler(self, broker):
        """测试 AI 报警消息处理器"""
        handler = AIAlertMessageHandler()
        broker.register_message_type("ai_alert", handler)
        
        received_messages = []
        broker.subscribe("ai_alert", lambda msg: received_messages.append(msg))
        
        # 有效的 AI 报警消息
        result = broker.publish("ai_alert", {
            "alert_type": "intrusion",
            "severity": "high",
            "timestamp": datetime.now().isoformat()
        })
        
        assert result.success is True
        assert len(received_messages) == 1


class TestBrokerStats:
    """测试统计信息"""
    
    def test_stats_tracking(self, broker):
        """测试统计信息跟踪"""
        handler = MockMessageHandler("test_type")
        broker.register_message_type("test_type", handler)
        
        broker.subscribe("test_type", lambda msg: None)
        
        stats = broker.get_stats()
        initial_published = stats["messages_published"]
        
        # 发布成功的消息
        broker.publish("test_type", {"value": "test"})
        
        stats = broker.get_stats()
        assert stats["messages_published"] == initial_published + 1
    
    def test_failed_message_stats(self, broker):
        """测试失败消息统计"""
        handler = MockMessageHandler("test_type")
        broker.register_message_type("test_type", handler)
        
        stats = broker.get_stats()
        initial_failed = stats["messages_failed"]
        
        # 发布无效消息
        broker.publish("test_type", {})  # 缺少 'value'
        
        stats = broker.get_stats()
        assert stats["messages_failed"] == initial_failed + 1
    
    def test_subscriber_count(self, broker):
        """测试订阅者计数"""
        handler = MockMessageHandler("test_type")
        broker.register_message_type("test_type", handler)
        
        assert broker.get_subscriber_count() == 0
        
        sub1 = broker.subscribe("test_type", lambda msg: None)
        assert broker.get_subscriber_count() == 1
        assert broker.get_subscriber_count("test_type") == 1
        
        sub2 = broker.subscribe("test_type", lambda msg: None)
        assert broker.get_subscriber_count() == 2
        assert broker.get_subscriber_count("test_type") == 2
        
        broker.unsubscribe("test_type", sub1)
        assert broker.get_subscriber_count() == 1


class TestThreadSafety:
    """测试线程安全"""
    
    def test_concurrent_publish(self, broker):
        """测试并发发布消息"""
        handler = MockMessageHandler("test_type")
        broker.register_message_type("test_type", handler)
        
        received_messages = []
        lock = threading.Lock()
        
        def callback(msg):
            with lock:
                received_messages.append(msg)
        
        broker.subscribe("test_type", callback)
        
        def publish_message(value):
            broker.publish("test_type", {"value": value})
        
        threads = [
            threading.Thread(target=publish_message, args=(f"msg_{i}",))
            for i in range(20)
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(received_messages) == 20
    
    def test_concurrent_subscribe_unsubscribe(self, broker):
        """测试并发订阅和取消订阅"""
        handler = MockMessageHandler("test_type")
        broker.register_message_type("test_type", handler)
        
        subscription_ids = []
        lock = threading.Lock()
        
        def subscribe_and_unsubscribe():
            sub_id = broker.subscribe("test_type", lambda msg: None)
            with lock:
                subscription_ids.append(sub_id)
            time.sleep(0.01)
            broker.unsubscribe("test_type", sub_id)
        
        threads = [
            threading.Thread(target=subscribe_and_unsubscribe)
            for _ in range(10)
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # 所有订阅都应该被取消
        assert broker.get_subscriber_count("test_type") == 0


class TestShutdown:
    """测试关闭和清理"""
    
    def test_shutdown_clears_resources(self, broker):
        """测试关闭清理所有资源"""
        handler = MockMessageHandler("test_type")
        broker.register_message_type("test_type", handler)
        broker.subscribe("test_type", lambda msg: None)
        
        assert broker.get_subscriber_count() > 0
        assert len(broker.get_registered_types()) > 0
        
        broker.shutdown()
        
        assert broker.get_subscriber_count() == 0
        assert len(broker.get_registered_types()) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
