"""
Test script for ErrorHandler implementation

验证错误处理机制的功能：
1. 验证错误处理
2. 数据库错误处理（重试机制）
3. 订阅者错误处理
"""

import sys
import time
from datetime import datetime

# 添加 src 到路径
sys.path.insert(0, 'src')

from broker import (
    MessageBroker,
    DirectionMessageHandler,
    AngleMessageHandler,
    ErrorHandler,
)
from broker.models import MessageData, ValidationResult


def test_validation_error_handling():
    """测试验证错误处理"""
    print("\n=== Test 1: Validation Error Handling ===")
    
    broker = MessageBroker.get_instance()
    
    # 注册消息类型（使用 allow_override 以防已注册）
    broker.register_message_type("direction_result", DirectionMessageHandler(), allow_override=True)
    broker.register_message_type("angle_value", AngleMessageHandler(), allow_override=True)
    
    # 测试无效的方向消息（缺少 command 字段）
    print("\n1. Testing invalid direction message (missing command)...")
    result = broker.publish("direction_result", {
        "timestamp": datetime.now().isoformat()
    })
    
    assert not result.success, "Should fail validation"
    assert len(result.errors) > 0, "Should have errors"
    print(f"✓ Validation failed as expected: {result.errors}")
    
    # 测试无效的角度消息（角度超出范围）
    print("\n2. Testing invalid angle message (out of range)...")
    result = broker.publish("angle_value", {
        "angle": 500.0,  # 超出有效范围
        "timestamp": datetime.now().isoformat()
    })
    
    assert not result.success, "Should fail validation"
    assert len(result.errors) > 0, "Should have errors"
    print(f"✓ Validation failed as expected: {result.errors}")
    
    # 测试有效消息
    print("\n3. Testing valid direction message...")
    result = broker.publish("direction_result", {
        "command": "forward",
        "timestamp": datetime.now().isoformat()
    })
    
    assert result.success, "Should succeed"
    print(f"✓ Valid message published successfully: {result.message_id}")
    
    print("\n✓ Validation error handling test passed!")


def test_database_error_handling():
    """测试数据库错误处理（重试机制）"""
    print("\n=== Test 2: Database Error Handling with Retry ===")
    
    error_handler = ErrorHandler()
    
    # 模拟数据库操作失败然后成功
    attempt_count = [0]
    
    def flaky_operation():
        """模拟不稳定的数据库操作"""
        attempt_count[0] += 1
        if attempt_count[0] < 2:
            raise Exception(f"Database connection failed (attempt {attempt_count[0]})")
        return {"data": "success", "attempt": attempt_count[0]}
    
    print("\n1. Testing retry mechanism with flaky operation...")
    result = error_handler.handle_database_error(
        operation=flaky_operation,
        operation_name="test_flaky_query",
        error=Exception("Initial failure"),
        max_retries=3,
        initial_delay=0.05  # 短延迟用于测试
    )
    
    assert result is not None, "Should succeed after retry"
    assert result["data"] == "success", "Should return correct data"
    assert attempt_count[0] == 2, "Should succeed on second attempt"
    print(f"✓ Operation succeeded after {attempt_count[0]} attempts: {result}")
    
    # 测试所有重试都失败的情况
    print("\n2. Testing all retries fail (should return cached/None)...")
    
    def always_fail():
        """总是失败的操作"""
        raise Exception("Permanent database failure")
    
    result = error_handler.handle_database_error(
        operation=always_fail,
        operation_name="test_permanent_failure",
        error=Exception("Initial failure"),
        max_retries=2,
        initial_delay=0.05
    )
    
    assert result is None, "Should return None when all retries fail"
    print("✓ Returned None after all retries failed (as expected)")
    
    # 测试缓存机制
    print("\n3. Testing cache mechanism...")
    
    # 先成功一次，缓存结果
    def successful_operation():
        return {"cached": "data"}
    
    result = error_handler.handle_database_error(
        operation=successful_operation,
        operation_name="test_cache",
        error=Exception("Initial failure"),
        max_retries=1
    )
    
    assert result == {"cached": "data"}, "Should return correct data"
    print(f"✓ Operation succeeded and cached: {result}")
    
    # 现在让操作失败，应该返回缓存
    result = error_handler.handle_database_error(
        operation=always_fail,
        operation_name="test_cache",
        error=Exception("Failure"),
        max_retries=1,
        initial_delay=0.05
    )
    
    assert result == {"cached": "data"}, "Should return cached data"
    print(f"✓ Returned cached data after failure: {result}")
    
    print("\n✓ Database error handling test passed!")


def test_subscriber_error_handling():
    """测试订阅者错误处理（错误隔离）"""
    print("\n=== Test 3: Subscriber Error Handling (Isolation) ===")
    
    broker = MessageBroker.get_instance()
    
    # 确保消息类型已注册
    if "direction_result" not in broker.get_registered_types():
        broker.register_message_type("direction_result", DirectionMessageHandler())
    
    # 记录回调执行情况
    callback_results = []
    
    def good_subscriber_1(message):
        """正常的订阅者"""
        callback_results.append(("good_1", message.message_id))
        print(f"  Good subscriber 1 received: {message.message_id}")
    
    def bad_subscriber(message):
        """会抛出异常的订阅者"""
        callback_results.append(("bad", message.message_id))
        print(f"  Bad subscriber received: {message.message_id}")
        raise Exception("Subscriber callback failed!")
    
    def good_subscriber_2(message):
        """另一个正常的订阅者"""
        callback_results.append(("good_2", message.message_id))
        print(f"  Good subscriber 2 received: {message.message_id}")
    
    # 订阅消息
    print("\n1. Subscribing three subscribers (one will fail)...")
    sub1 = broker.subscribe("direction_result", good_subscriber_1)
    sub2 = broker.subscribe("direction_result", bad_subscriber)
    sub3 = broker.subscribe("direction_result", good_subscriber_2)
    
    print(f"✓ Subscribed: {sub1}, {sub2}, {sub3}")
    
    # 发布消息
    print("\n2. Publishing message (bad subscriber will fail)...")
    callback_results.clear()
    
    result = broker.publish("direction_result", {
        "command": "forward",
        "timestamp": datetime.now().isoformat()
    })
    
    # 验证结果
    assert result.success, "Message should be published successfully"
    assert result.subscribers_notified == 2, "Should notify 2 subscribers (bad one failed)"
    
    # 验证所有订阅者都被调用（包括失败的）
    assert len(callback_results) == 3, "All subscribers should be called"
    assert ("good_1", result.message_id) in callback_results
    assert ("bad", result.message_id) in callback_results
    assert ("good_2", result.message_id) in callback_results
    
    print(f"✓ Message published: {result.message_id}")
    print(f"✓ Notified {result.subscribers_notified} subscribers successfully")
    print(f"✓ All 3 subscribers were called (1 failed but didn't affect others)")
    
    # 清理
    broker.unsubscribe("direction_result", sub1)
    broker.unsubscribe("direction_result", sub2)
    broker.unsubscribe("direction_result", sub3)
    
    print("\n✓ Subscriber error handling test passed!")


def test_error_handler_direct():
    """直接测试 ErrorHandler 类的方法"""
    print("\n=== Test 4: Direct ErrorHandler Methods ===")
    
    error_handler = ErrorHandler()
    
    # 测试 handle_validation_error
    print("\n1. Testing handle_validation_error...")
    message = MessageData(
        type="test",
        data={"test": "data"},
        timestamp=datetime.now()
    )
    validation_result = ValidationResult(
        valid=False,
        errors=["Missing field: command"],
        warnings=[]
    )
    
    # 应该记录错误但不抛出异常
    error_handler.handle_validation_error(message, validation_result)
    print("✓ Validation error handled (logged)")
    
    # 测试 handle_subscriber_error
    print("\n2. Testing handle_subscriber_error...")
    error_handler.handle_subscriber_error(
        subscriber_id="test_sub_123",
        error=Exception("Test error"),
        message_id="msg_456"
    )
    print("✓ Subscriber error handled (logged)")
    
    # 测试缓存清理
    print("\n3. Testing cache clear...")
    error_handler._cache["test_key"] = "test_value"
    assert "test_key" in error_handler._cache
    error_handler.clear_cache()
    assert len(error_handler._cache) == 0
    print("✓ Cache cleared successfully")
    
    print("\n✓ Direct ErrorHandler methods test passed!")


def main():
    """运行所有测试"""
    print("=" * 60)
    print("ErrorHandler Implementation Test Suite")
    print("=" * 60)
    
    try:
        test_validation_error_handling()
        test_database_error_handling()
        test_subscriber_error_handling()
        test_error_handler_direct()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
