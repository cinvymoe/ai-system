"""
Integration test for MotionDirectionProcessor with MessageBroker

验证 MotionDirectionProcessor 与 MessageBroker 的集成
"""

import asyncio
import sys
from pathlib import Path

# Add backend/src and parent directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))
sys.path.insert(0, str(Path(__file__).parent.parent))  # For datahandler

from collectors.sensors.mock_sensor import MockSensorDevice
from collectors.processors.motion_processor import MotionDirectionProcessor
from broker.broker import MessageBroker
from broker.handlers import DirectionMessageHandler


async def test_integration():
    """测试 MotionDirectionProcessor 与 MessageBroker 的集成"""
    
    print("=" * 60)
    print("测试 MotionDirectionProcessor 与 MessageBroker 集成")
    print("=" * 60)
    
    # 初始化消息代理
    broker = MessageBroker.get_instance()
    
    # 注册方向消息处理器
    direction_handler = DirectionMessageHandler()
    broker.register_message_type('direction_result', direction_handler)
    print("✓ 消息代理已初始化，方向消息处理器已注册")
    
    # 创建订阅者来验证消息发布
    received_messages = []
    
    def message_subscriber(message_data):
        """订阅者回调函数"""
        received_messages.append(message_data)
        print(f"  📨 收到消息: {message_data.data['command']} "
              f"(强度: {message_data.data['intensity']:.4f})")
    
    # 订阅方向消息
    subscription_id = broker.subscribe('direction_result', message_subscriber)
    print(f"✓ 已订阅方向消息 (订阅ID: {subscription_id})")
    
    # 创建运动方向处理器
    processor = MotionDirectionProcessor()
    print("✓ MotionDirectionProcessor 已创建")
    
    # 测试不同的运动模式
    patterns = ['forward', 'turn_left', 'stationary']
    
    for pattern in patterns:
        print(f"\n{'=' * 40}")
        print(f"测试运动模式: {pattern}")
        print(f"{'=' * 40}")
        
        # 创建模拟传感器
        sensor = MockSensorDevice(
            sensor_id=f'test_sensor_{pattern}',
            motion_pattern=pattern,
            config={'interval': 0.1, 'noise_level': 0.01}
        )
        
        # 连接传感器
        connected = await sensor.connect()
        if not connected:
            print(f"✗ 无法连接传感器")
            continue
        
        print(f"✓ 传感器已连接")
        
        # 处理3个数据样本
        messages_before = len(received_messages)
        
        for i in range(3):
            try:
                # 读取传感器数据
                sensor_data = await sensor.read_sensor_data()
                
                # 处理数据（这会自动发布消息到代理）
                motion_command = processor.process(sensor_data)
                
                print(f"  样本 {i+1}: {motion_command.command} "
                      f"(强度: {motion_command.intensity:.4f})")
                
                # 等待一小段时间
                await asyncio.sleep(0.1)
                
            except Exception as e:
                print(f"✗ 处理数据时出错: {e}")
        
        # 断开传感器
        await sensor.disconnect()
        
        # 验证消息发布
        messages_after = len(received_messages)
        messages_published = messages_after - messages_before
        
        print(f"✓ 发布了 {messages_published} 条消息到消息代理")
        
        # 重置处理器状态
        processor.reset()
    
    # 取消订阅
    broker.unsubscribe('direction_result', subscription_id)
    print(f"\n✓ 已取消订阅")
    
    # 显示统计信息
    stats = broker.get_stats()
    print(f"\n消息代理统计:")
    print(f"  发布的消息: {stats['messages_published']}")
    print(f"  失败的消息: {stats['messages_failed']}")
    print(f"  订阅者数量: {stats['subscribers_count']}")
    
    print(f"\n总共收到 {len(received_messages)} 条消息")
    
    print(f"\n{'=' * 60}")
    print("集成测试完成 ✓")
    print(f"{'=' * 60}")


if __name__ == '__main__':
    # 运行集成测试
    asyncio.run(test_integration())