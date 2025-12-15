"""
Test Broker Logging Configuration

测试消息代理的日志记录功能。

实现要求：
- Requirements 8.1: 记录消息发布日志
- Requirements 8.2: 记录订阅注册日志
- Requirements 8.3: 记录错误日志
- Requirements 8.4: 支持可配置日志级别
"""

import sys
import logging
import tempfile
import json
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

try:
    from src.broker import (
        MessageBroker,
        DirectionMessageHandler,
        AngleMessageHandler,
        configure_broker_logging,
        get_broker_logger,
        create_message_logger,
        create_subscriber_logger,
    )
    from src.broker.logging_config import StructuredFormatter
except ImportError:
    from broker import (
        MessageBroker,
        DirectionMessageHandler,
        AngleMessageHandler,
        configure_broker_logging,
        get_broker_logger,
        create_message_logger,
        create_subscriber_logger,
    )
    from broker.logging_config import StructuredFormatter


def test_basic_logging_configuration():
    """测试基本日志配置"""
    print("\n=== 测试 1: 基本日志配置 ===")
    
    # 配置日志
    configure_broker_logging(log_level="INFO", use_structured=False)
    
    # 获取日志记录器
    logger = get_broker_logger("test")
    
    # 测试不同级别的日志
    logger.debug("这是 DEBUG 日志（不应显示）")
    logger.info("这是 INFO 日志")
    logger.warning("这是 WARNING 日志")
    logger.error("这是 ERROR 日志")
    
    print("✓ 基本日志配置测试通过")


def test_configurable_log_levels():
    """测试可配置的日志级别 (Requirement 8.4)"""
    print("\n=== 测试 2: 可配置日志级别 ===")
    
    # 测试 DEBUG 级别
    print("\n--- DEBUG 级别 ---")
    configure_broker_logging(log_level="DEBUG", use_structured=False)
    logger = get_broker_logger("test_debug")
    logger.debug("DEBUG 级别日志应该显示")
    logger.info("INFO 级别日志应该显示")
    
    # 测试 WARNING 级别
    print("\n--- WARNING 级别 ---")
    configure_broker_logging(log_level="WARNING", use_structured=False)
    logger = get_broker_logger("test_warning")
    logger.info("INFO 级别日志不应显示")
    logger.warning("WARNING 级别日志应该显示")
    logger.error("ERROR 级别日志应该显示")
    
    # 测试 ERROR 级别
    print("\n--- ERROR 级别 ---")
    configure_broker_logging(log_level="ERROR", use_structured=False)
    logger = get_broker_logger("test_error")
    logger.warning("WARNING 级别日志不应显示")
    logger.error("ERROR 级别日志应该显示")
    
    print("\n✓ 可配置日志级别测试通过")


def test_structured_logging():
    """测试结构化日志（JSON 格式）"""
    print("\n=== 测试 3: 结构化日志 ===")
    
    # 配置结构化日志
    configure_broker_logging(log_level="INFO", use_structured=True)
    
    logger = get_broker_logger("test_structured")
    
    print("\n--- JSON 格式日志 ---")
    logger.info("这是结构化日志消息")
    logger.info("带上下文的日志", extra={
        "message_id": "msg_123",
        "message_type": "direction_result",
        "custom_field": "custom_value"
    })
    
    print("\n✓ 结构化日志测试通过")


def test_message_publish_logging():
    """测试消息发布日志 (Requirement 8.1)"""
    print("\n=== 测试 4: 消息发布日志 ===")
    
    # 配置日志
    configure_broker_logging(log_level="INFO", use_structured=False)
    
    # 创建消息代理
    broker = MessageBroker.get_instance()
    
    # 注册消息类型
    broker.register_message_type("direction_result", DirectionMessageHandler())
    broker.register_message_type("angle_value", AngleMessageHandler())
    
    print("\n--- 发布有效消息 ---")
    result = broker.publish("direction_result", {
        "command": "forward",
        "timestamp": "2024-01-01T00:00:00",
        "intensity": 0.8
    })
    print(f"发布结果: success={result.success}, message_id={result.message_id}")
    
    print("\n--- 发布无效消息 ---")
    result = broker.publish("direction_result", {
        "command": "invalid_command",  # 无效命令
        "timestamp": "2024-01-01T00:00:00"
    })
    print(f"发布结果: success={result.success}, errors={result.errors}")
    
    print("\n✓ 消息发布日志测试通过")


def test_subscription_logging():
    """测试订阅注册日志 (Requirement 8.2)"""
    print("\n=== 测试 5: 订阅注册日志 ===")
    
    # 配置日志
    configure_broker_logging(log_level="INFO", use_structured=False)
    
    # 创建消息代理
    broker = MessageBroker.get_instance()
    
    # 确保消息类型已注册
    if "direction_result" not in broker.get_registered_types():
        broker.register_message_type("direction_result", DirectionMessageHandler())
    
    print("\n--- 注册订阅者 ---")
    
    def callback1(message):
        print(f"  回调1收到消息: {message.message_id}")
    
    def callback2(message):
        print(f"  回调2收到消息: {message.message_id}")
    
    sub_id1 = broker.subscribe("direction_result", callback1)
    print(f"订阅者1注册: {sub_id1}")
    
    sub_id2 = broker.subscribe("direction_result", callback2)
    print(f"订阅者2注册: {sub_id2}")
    
    print("\n--- 取消订阅 ---")
    success = broker.unsubscribe("direction_result", sub_id1)
    print(f"取消订阅结果: {success}")
    
    print("\n✓ 订阅注册日志测试通过")


def test_error_logging():
    """测试错误日志 (Requirement 8.3)"""
    print("\n=== 测试 6: 错误日志 ===")
    
    # 配置日志
    configure_broker_logging(log_level="INFO", use_structured=False)
    
    # 创建消息代理
    broker = MessageBroker.get_instance()
    
    # 确保消息类型已注册
    if "direction_result" not in broker.get_registered_types():
        broker.register_message_type("direction_result", DirectionMessageHandler())
    
    print("\n--- 验证错误 ---")
    result = broker.publish("direction_result", {
        # 缺少必需字段 'command'
        "timestamp": "2024-01-01T00:00:00"
    })
    print(f"验证错误: {result.errors}")
    
    print("\n--- 订阅者错误 ---")
    
    def failing_callback(message):
        raise Exception("订阅者回调故意失败")
    
    def working_callback(message):
        print(f"  正常回调收到消息: {message.message_id}")
    
    broker.subscribe("direction_result", failing_callback)
    broker.subscribe("direction_result", working_callback)
    
    # 发布消息，应该记录订阅者错误但不影响其他订阅者
    result = broker.publish("direction_result", {
        "command": "forward",
        "timestamp": "2024-01-01T00:00:00"
    })
    print(f"发布结果: success={result.success}, notified={result.subscribers_notified}")
    
    print("\n✓ 错误日志测试通过")


def test_context_loggers():
    """测试上下文日志记录器"""
    print("\n=== 测试 7: 上下文日志记录器 ===")
    
    # 配置日志
    configure_broker_logging(log_level="INFO", use_structured=True)
    
    print("\n--- 消息上下文日志 ---")
    msg_logger = create_message_logger(
        message_id="msg_12345",
        message_type="direction_result"
    )
    msg_logger.info("这是带消息上下文的日志")
    
    print("\n--- 订阅者上下文日志 ---")
    sub_logger = create_subscriber_logger(
        subscriber_id="sub_67890"
    )
    sub_logger.info("这是带订阅者上下文的日志")
    
    print("\n✓ 上下文日志记录器测试通过")


def test_file_logging():
    """测试文件日志输出"""
    print("\n=== 测试 8: 文件日志输出 ===")
    
    # 创建临时日志文件
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
        log_file = f.name
    
    try:
        # 配置文件日志
        configure_broker_logging(
            log_level="INFO",
            use_structured=False,
            log_file=log_file
        )
        
        logger = get_broker_logger("test_file")
        logger.info("这条日志应该写入文件")
        logger.warning("这是警告日志")
        logger.error("这是错误日志")
        
        # 读取日志文件
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"\n--- 日志文件内容 ({log_file}) ---")
        print(content)
        
        # 验证日志内容
        assert "这条日志应该写入文件" in content
        assert "这是警告日志" in content
        assert "这是错误日志" in content
        
        print("\n✓ 文件日志输出测试通过")
        
    finally:
        # 清理临时文件
        import os
        if os.path.exists(log_file):
            os.remove(log_file)


def test_high_frequency_logging():
    """测试高频消息日志性能 (Requirement 8.5)"""
    print("\n=== 测试 9: 高频消息日志性能 ===")
    
    # 配置日志
    configure_broker_logging(log_level="INFO", use_structured=False)
    
    # 创建消息代理
    broker = MessageBroker.get_instance()
    
    # 确保消息类型已注册
    if "direction_result" not in broker.get_registered_types():
        broker.register_message_type("direction_result", DirectionMessageHandler())
    
    import time
    
    print("\n--- 发布100条消息 ---")
    start_time = time.time()
    
    for i in range(100):
        broker.publish("direction_result", {
            "command": "forward",
            "timestamp": "2024-01-01T00:00:00",
            "intensity": 0.5
        })
    
    elapsed = time.time() - start_time
    print(f"发布100条消息耗时: {elapsed:.4f}秒")
    print(f"平均每条消息: {elapsed/100*1000:.2f}毫秒")
    
    # 性能应该合理（每条消息不超过10ms）
    assert elapsed / 100 < 0.01, "日志性能不佳"
    
    print("\n✓ 高频消息日志性能测试通过")


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("消息代理日志功能测试")
    print("=" * 60)
    
    try:
        test_basic_logging_configuration()
        test_configurable_log_levels()
        test_structured_logging()
        test_message_publish_logging()
        test_subscription_logging()
        test_error_logging()
        test_context_loggers()
        test_file_logging()
        test_high_frequency_logging()
        
        print("\n" + "=" * 60)
        print("✓ 所有测试通过！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
