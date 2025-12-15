"""
Test dynamic message type registration functionality.

Tests Requirements 6.1-6.5:
- 6.1: Generic interface for registering new message types
- 6.2: Create dedicated subscription channel
- 6.3: Support dynamic addition without code modification
- 6.4: Allow custom validation rules
- 6.5: Backward compatibility when extending
"""

import pytest
from typing import Dict, Any
from datetime import datetime

from src.broker.broker import MessageBroker
from src.broker.handlers import MessageTypeHandler
from src.broker.models import ValidationResult, ProcessedMessage, MessageData
from src.broker.errors import MessageTypeError


class CustomMessageHandler(MessageTypeHandler):
    """自定义消息处理器用于测试"""
    
    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """自定义验证规则"""
        errors = []
        
        if 'custom_field' not in data:
            errors.append("Missing required field: 'custom_field'")
        
        if 'value' in data and not isinstance(data['value'], (int, float)):
            errors.append("Field 'value' must be a number")
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=[]
        )
    
    def process(self, data: Dict[str, Any]) -> ProcessedMessage:
        """处理自定义消息"""
        message = MessageData(
            type=self.get_type_name(),
            data=data,
            timestamp=datetime.now()
        )
        
        return ProcessedMessage(
            original=message,
            validated=True,
            cameras=[],
            processing_time=0.0,
            errors=[]
        )
    
    def get_type_name(self) -> str:
        return "custom_type"


class AnotherCustomHandler(MessageTypeHandler):
    """另一个自定义处理器"""
    
    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        return ValidationResult(valid=True, errors=[], warnings=[])
    
    def process(self, data: Dict[str, Any]) -> ProcessedMessage:
        message = MessageData(
            type=self.get_type_name(),
            data=data,
            timestamp=datetime.now()
        )
        return ProcessedMessage(
            original=message,
            validated=True,
            cameras=[],
            processing_time=0.0,
            errors=[]
        )
    
    def get_type_name(self) -> str:
        return "another_custom_type"


def test_register_new_message_type():
    """测试注册新消息类型 (Requirement 6.1)"""
    broker = MessageBroker.get_instance()
    handler = CustomMessageHandler()
    
    # 注册新类型
    broker.register_message_type("custom_type", handler)
    
    # 验证类型已注册
    assert broker.is_type_registered("custom_type")
    assert "custom_type" in broker.get_registered_types()
    
    # 验证可以获取处理器
    retrieved_handler = broker.get_handler("custom_type")
    assert retrieved_handler is handler


def test_dedicated_subscription_channel(broker_instance):
    """测试创建专用订阅通道 (Requirement 6.2)"""
    handler = CustomMessageHandler()
    broker_instance.register_message_type("test_channel", handler)
    
    # 验证可以订阅新类型
    callback_called = []
    
    def callback(msg):
        callback_called.append(msg)
    
    sub_id = broker_instance.subscribe("test_channel", callback)
    assert sub_id is not None
    
    # 发布消息
    result = broker_instance.publish("test_channel", {
        "custom_field": "test",
        "value": 42
    })
    
    assert result.success
    assert len(callback_called) == 1


def test_dynamic_addition_without_modification(broker_instance):
    """测试动态添加消息类型无需修改核心代码 (Requirement 6.3)"""
    # 在运行时注册多个新类型
    handler1 = CustomMessageHandler()
    handler2 = AnotherCustomHandler()
    
    initial_types = set(broker_instance.get_registered_types())
    
    # 动态注册
    broker_instance.register_message_type("runtime_type_1", handler1)
    broker_instance.register_message_type("runtime_type_2", handler2)
    
    # 验证新类型已添加
    current_types = set(broker_instance.get_registered_types())
    assert "runtime_type_1" in current_types
    assert "runtime_type_2" in current_types
    
    # 验证可以立即使用
    result1 = broker_instance.publish("runtime_type_1", {
        "custom_field": "test1",
        "value": 100
    })
    result2 = broker_instance.publish("runtime_type_2", {
        "any_field": "test2"
    })
    
    assert result1.success
    assert result2.success


def test_custom_validation_rules(broker_instance):
    """测试自定义验证规则 (Requirement 6.4)"""
    handler = CustomMessageHandler()
    broker_instance.register_message_type("validated_type", handler)
    
    # 测试有效数据
    result_valid = broker_instance.publish("validated_type", {
        "custom_field": "present",
        "value": 123
    })
    assert result_valid.success
    
    # 测试缺少必需字段
    result_missing = broker_instance.publish("validated_type", {
        "value": 456
    })
    assert not result_missing.success
    assert any("custom_field" in err for err in result_missing.errors)
    
    # 测试无效类型
    result_invalid = broker_instance.publish("validated_type", {
        "custom_field": "present",
        "value": "not_a_number"
    })
    assert not result_invalid.success
    assert any("number" in err.lower() for err in result_invalid.errors)


def test_backward_compatibility(broker_instance):
    """测试向后兼容性 (Requirement 6.5)"""
    handler1 = CustomMessageHandler()
    broker_instance.register_message_type("compat_type", handler1)
    
    # 创建订阅者
    messages_received = []
    
    def callback(msg):
        messages_received.append(msg)
    
    sub_id = broker_instance.subscribe("compat_type", callback)
    
    # 发布消息
    broker_instance.publish("compat_type", {
        "custom_field": "test1",
        "value": 1
    })
    
    assert len(messages_received) == 1
    
    # 现在覆盖处理器（使用 allow_override）
    handler2 = AnotherCustomHandler()
    broker_instance.register_message_type("compat_type", handler2, allow_override=True)
    
    # 验证订阅者仍然有效（向后兼容）
    broker_instance.publish("compat_type", {
        "any_field": "test2"
    })
    
    # 订阅者应该收到第二条消息
    assert len(messages_received) == 2


def test_prevent_duplicate_registration():
    """测试防止重复注册（不使用 allow_override）"""
    broker = MessageBroker.get_instance()
    handler = CustomMessageHandler()
    
    # 首次注册
    broker.register_message_type("duplicate_test", handler)
    
    # 尝试再次注册应该失败
    with pytest.raises(MessageTypeError) as exc_info:
        broker.register_message_type("duplicate_test", handler)
    
    assert "already registered" in str(exc_info.value)


def test_allow_override_flag(broker_instance):
    """测试 allow_override 标志"""
    handler1 = CustomMessageHandler()
    handler2 = AnotherCustomHandler()
    
    # 首次注册
    broker_instance.register_message_type("override_test", handler1)
    
    # 使用 allow_override=True 覆盖
    broker_instance.register_message_type("override_test", handler2, allow_override=True)
    
    # 验证处理器已更新
    current_handler = broker_instance.get_handler("override_test")
    assert current_handler is handler2


def test_unregister_message_type(broker_instance):
    """测试注销消息类型"""
    handler = CustomMessageHandler()
    broker_instance.register_message_type("unregister_test", handler)
    
    # 验证已注册
    assert broker_instance.is_type_registered("unregister_test")
    
    # 注销
    result = broker_instance.unregister_message_type("unregister_test")
    assert result is True
    
    # 验证已注销
    assert not broker_instance.is_type_registered("unregister_test")
    
    # 尝试注销不存在的类型
    result = broker_instance.unregister_message_type("nonexistent")
    assert result is False


def test_handler_interface_validation(broker_instance):
    """测试处理器接口验证"""
    
    class InvalidHandler:
        """缺少必需方法的处理器"""
        pass
    
    # 尝试注册无效处理器
    with pytest.raises(MessageTypeError) as exc_info:
        broker_instance.register_message_type("invalid", InvalidHandler())
    
    assert "must implement" in str(exc_info.value)


def test_multiple_types_isolation(broker_instance):
    """测试多个消息类型的隔离性"""
    handler1 = CustomMessageHandler()
    handler2 = AnotherCustomHandler()
    
    broker_instance.register_message_type("type_a", handler1)
    broker_instance.register_message_type("type_b", handler2)
    
    # 为每个类型创建订阅者
    type_a_messages = []
    type_b_messages = []
    
    def callback_a(msg):
        type_a_messages.append(msg)
    
    def callback_b(msg):
        type_b_messages.append(msg)
    
    broker_instance.subscribe("type_a", callback_a)
    broker_instance.subscribe("type_b", callback_b)
    
    # 发布到 type_a
    broker_instance.publish("type_a", {"custom_field": "a", "value": 1})
    
    # 发布到 type_b
    broker_instance.publish("type_b", {"any_field": "b"})
    
    # 验证隔离性
    assert len(type_a_messages) == 1
    assert len(type_b_messages) == 1
    assert type_a_messages[0].type == "type_a"
    assert type_b_messages[0].type == "type_b"


# Fixtures

@pytest.fixture
def broker_instance():
    """创建一个新的 broker 实例用于测试"""
    # 重置单例以获得干净的实例
    MessageBroker._instance = None
    broker = MessageBroker.get_instance()
    yield broker
    # 清理
    broker.shutdown()
    MessageBroker._instance = None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
