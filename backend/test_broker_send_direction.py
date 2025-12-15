"""
发送方向消息到 Broker

用于测试 broker 订阅功能
"""

import sys
import asyncio
from datetime import datetime

# Add src to path
sys.path.insert(0, 'src')

from broker.broker import MessageBroker
from broker.handlers import DirectionMessageHandler
from broker.mapper import CameraMapper
from database import get_db


async def send_direction_message(direction: str, intensity: float = 0.8):
    """发送方向消息"""
    print(f"\n发送方向消息: {direction} (强度: {intensity})")
    
    # 获取消息代理实例
    broker = MessageBroker.get_instance()
    
    # 设置摄像头映射器
    camera_mapper = CameraMapper(db_session_factory=get_db)
    broker.set_camera_mapper(camera_mapper)
    
    # 注册方向消息处理器（如果还没注册）
    if "direction_result" not in broker.get_registered_types():
        broker.register_message_type("direction_result", DirectionMessageHandler())
    
    # 发布消息
    result = broker.publish("direction_result", {
        "command": direction,
        "intensity": intensity,
        "timestamp": datetime.now().isoformat()
    })
    
    if result.success:
        print(f"✓ 消息发送成功")
        print(f"  消息 ID: {result.message_id}")
        print(f"  通知订阅者: {result.subscribers_notified} 个")
    else:
        print(f"✗ 消息发送失败")
        print(f"  错误: {result.errors}")
    
    return result


async def main():
    """主函数"""
    print("=" * 60)
    print("  Broker 方向消息发送工具")
    print("=" * 60)
    
    if len(sys.argv) < 2:
        print("\n用法:")
        print("  python test_broker_send_direction.py <direction> [intensity]")
        print("\n可用方向:")
        print("  - forward      (前进)")
        print("  - backward     (后退)")
        print("  - turn_left    (左转)")
        print("  - turn_right   (右转)")
        print("  - stationary   (静止)")
        print("\n示例:")
        print("  python test_broker_send_direction.py forward")
        print("  python test_broker_send_direction.py turn_left 0.6")
        sys.exit(1)
    
    direction = sys.argv[1]
    intensity = float(sys.argv[2]) if len(sys.argv) > 2 else 0.8
    
    try:
        await send_direction_message(direction, intensity)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
