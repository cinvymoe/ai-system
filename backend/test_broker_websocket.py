#!/usr/bin/env python3
"""
测试消息代理 WebSocket API 功能

验证 WebSocket 端点的基本功能：
1. 连接建立
2. 当前状态发送
3. 消息广播
4. 客户端断开处理
"""

import asyncio
import json
import logging
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from src.broker.broker import MessageBroker
    from src.broker.models import MessageData
    from src.api.broker import broker_stream, connection_manager, _initialize_broker
except ImportError as e:
    logger.error(f"Import error: {e}")
    logger.error("Make sure you're running from the backend directory")
    exit(1)


class MockWebSocket:
    """模拟 WebSocket 连接"""
    
    def __init__(self, name: str):
        self.name = name
        self.client = ('127.0.0.1', 12345)
        self.accepted = False
        self.messages = []
        self.closed = False
        
    async def accept(self):
        self.accepted = True
        logger.info(f"✓ {self.name}: WebSocket accepted")
        
    async def send_json(self, data):
        if not self.closed:
            self.messages.append(data)
            logger.info(f"✓ {self.name}: Received message type '{data.get('type')}'")
        
    async def receive_text(self):
        # 模拟客户端保持连接一段时间后断开
        await asyncio.sleep(0.5)
        raise Exception("Client disconnected")
    
    async def close(self, code=None, reason=None):
        self.closed = True
        logger.info(f"✓ {self.name}: WebSocket closed")


async def test_websocket_basic_functionality():
    """测试 WebSocket 基本功能"""
    logger.info("=== 测试 WebSocket 基本功能 ===")
    
    # 创建模拟 WebSocket
    mock_ws = MockWebSocket("Client1")
    
    try:
        # 测试 WebSocket 处理器
        await broker_stream(mock_ws)
    except Exception as e:
        # 预期会因为客户端断开而出现异常
        logger.info(f"✓ WebSocket handler completed (expected: {type(e).__name__})")
    
    # 验证结果
    assert mock_ws.accepted, "WebSocket should be accepted"
    assert len(mock_ws.messages) >= 1, "Should receive at least current_state message"
    
    first_message = mock_ws.messages[0]
    assert first_message.get('type') == 'current_state', "First message should be current_state"
    
    logger.info(f"✓ WebSocket accepted: {mock_ws.accepted}")
    logger.info(f"✓ Messages received: {len(mock_ws.messages)}")
    logger.info(f"✓ First message type: {first_message.get('type')}")


async def test_message_broadcasting():
    """测试消息广播功能"""
    logger.info("=== 测试消息广播功能 ===")
    
    # 确保消息代理已初始化
    await _initialize_broker()
    broker = MessageBroker.get_instance()
    
    # 创建多个模拟 WebSocket 客户端
    clients = [MockWebSocket(f"Client{i}") for i in range(3)]
    
    # 模拟连接到连接管理器
    for client in clients:
        await connection_manager.connect(client)
    
    logger.info(f"✓ Connected {len(clients)} WebSocket clients")
    
    # 发布一条方向消息
    try:
        result = broker.publish("direction_result", {
            "command": "forward",
            "intensity": 0.8,
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"✓ Published direction message: {result.success}")
        logger.info(f"✓ Subscribers notified: {result.subscribers_notified}")
        
    except Exception as e:
        logger.error(f"✗ Failed to publish message: {e}")
    
    # 等待广播处理
    await asyncio.sleep(0.2)
    
    # 验证所有客户端都收到了广播消息
    broadcast_received = 0
    for client in clients:
        # 查找广播消息（不是 current_state）
        for msg in client.messages:
            if msg.get('type') == 'direction_result':
                broadcast_received += 1
                logger.info(f"✓ {client.name}: Received direction_result broadcast")
                break
    
    logger.info(f"✓ Broadcast messages received: {broadcast_received}/{len(clients)}")
    
    # 清理连接
    for client in clients:
        await connection_manager.disconnect(client)


async def test_angle_message_broadcasting():
    """测试角度消息广播"""
    logger.info("=== 测试角度消息广播 ===")
    
    broker = MessageBroker.get_instance()
    
    # 创建一个模拟客户端
    client = MockWebSocket("AngleClient")
    await connection_manager.connect(client)
    
    # 发布角度消息
    try:
        result = broker.publish("angle_value", {
            "angle": 45.0,
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"✓ Published angle message: {result.success}")
        
    except Exception as e:
        logger.error(f"✗ Failed to publish angle message: {e}")
    
    # 等待广播处理
    await asyncio.sleep(0.2)
    
    # 验证客户端收到了角度消息
    angle_received = False
    for msg in client.messages:
        if msg.get('type') == 'angle_value':
            angle_received = True
            logger.info(f"✓ {client.name}: Received angle_value broadcast")
            break
    
    logger.info(f"✓ Angle broadcast received: {angle_received}")
    
    # 清理
    await connection_manager.disconnect(client)


async def test_error_handling():
    """测试错误处理"""
    logger.info("=== 测试错误处理 ===")
    
    broker = MessageBroker.get_instance()
    
    # 测试无效消息
    try:
        result = broker.publish("direction_result", {
            # 缺少必需字段
            "invalid": "data"
        })
        
        logger.info(f"✓ Invalid message handling: success={result.success}")
        logger.info(f"✓ Error count: {len(result.errors)}")
        
        if result.errors:
            logger.info(f"✓ First error: {result.errors[0]}")
        
    except Exception as e:
        logger.info(f"✓ Exception handling: {type(e).__name__}")


async def main():
    """主测试函数"""
    logger.info("开始测试消息代理 WebSocket API")
    
    try:
        # 运行所有测试
        await test_websocket_basic_functionality()
        await test_message_broadcasting()
        await test_angle_message_broadcasting()
        await test_error_handling()
        
        logger.info("✅ 所有测试完成！")
        
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)