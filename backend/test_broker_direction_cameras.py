"""
测试 Broker 订阅方向消息并输出摄像头 URL

功能：
1. 订阅 direction_result 消息类型
2. 当收到方向消息时，输出对应的摄像头列表和 URL
3. 测试不同方向的摄像头映射
"""

import sys
import asyncio
import time
from datetime import datetime
from typing import List

# Add src to path
sys.path.insert(0, 'src')

from broker.broker import MessageBroker
from broker.handlers import DirectionMessageHandler
from broker.models import MessageData, CameraInfo
from broker.mapper import CameraMapper
from database import get_db


def print_separator(title: str = ""):
    """打印分隔线"""
    if title:
        print(f"\n{'=' * 60}")
        print(f"  {title}")
        print(f"{'=' * 60}")
    else:
        print(f"{'=' * 60}")


async def initialize_broker():
    """初始化消息代理"""
    print_separator("初始化消息代理")
    
    # 获取消息代理实例
    broker = MessageBroker.get_instance()
    
    # 设置摄像头映射器
    camera_mapper = CameraMapper(db_session_factory=get_db)
    broker.set_camera_mapper(camera_mapper)
    
    # 注册方向消息处理器（如果还没注册）
    if "direction_result" not in broker.get_registered_types():
        broker.register_message_type("direction_result", DirectionMessageHandler())
        print("✓ 已注册 direction_result 消息类型")
    else:
        print("ℹ direction_result 消息类型已注册")
    
    print("✓ 消息代理初始化完成")
    print(f"  - 已注册消息类型: {broker.get_registered_types()}")
    
    return broker, camera_mapper


def create_direction_callback(camera_mapper: CameraMapper):
    """创建方向消息回调函数"""
    
    def callback(message: MessageData):
        """处理方向消息并输出摄像头信息"""
        print_separator(f"收到方向消息: {message.message_id}")
        
        # 输出消息基本信息
        print(f"消息类型: {message.type}")
        print(f"时间戳: {message.timestamp}")
        print(f"消息数据: {message.data}")
        
        # 获取方向
        direction = message.data.get("command")
        if not direction:
            print("⚠ 警告: 消息中没有方向信息")
            return
        
        print(f"\n方向: {direction}")
        
        # 获取对应的摄像头列表
        try:
            cameras = camera_mapper.get_cameras_by_direction(direction)
            
            if not cameras:
                print(f"  ℹ 该方向没有关联的摄像头")
                return
            
            print(f"\n关联的摄像头数量: {len(cameras)}")
            print("-" * 60)
            
            # 输出每个摄像头的详细信息
            for i, camera in enumerate(cameras, 1):
                print(f"\n摄像头 #{i}:")
                print(f"  ID:     {camera.id}")
                print(f"  名称:   {camera.name}")
                print(f"  URL:    {camera.url}")
                print(f"  状态:   {camera.status}")
                if camera.directions:
                    print(f"  方向:   {', '.join(camera.directions)}")
            
            print("-" * 60)
            
        except Exception as e:
            print(f"✗ 获取摄像头信息时出错: {e}")
            import traceback
            traceback.print_exc()
    
    return callback


async def test_direction_subscription():
    """测试方向订阅功能"""
    print_separator("测试方向订阅功能")
    
    # 初始化
    broker, camera_mapper = await initialize_broker()
    
    # 创建并注册回调函数
    callback = create_direction_callback(camera_mapper)
    subscription_id = broker.subscribe("direction_result", callback)
    
    print(f"\n✓ 已订阅 direction_result 消息")
    print(f"  订阅 ID: {subscription_id}")
    print(f"  当前订阅数: {broker.get_subscriber_count('direction_result')}")
    
    # 测试不同的方向
    test_directions = [
        {"command": "forward", "intensity": 0.8},
        {"command": "backward", "intensity": 0.6},
        {"command": "turn_left", "intensity": 0.7},
        {"command": "turn_right", "intensity": 0.7},
        {"command": "stop", "intensity": 0.0},
    ]
    
    print_separator("发布测试消息")
    
    for direction_data in test_directions:
        print(f"\n>>> 发布方向消息: {direction_data['command']}")
        
        # 发布消息
        result = broker.publish("direction_result", {
            **direction_data,
            "timestamp": datetime.now().isoformat()
        })
        
        print(f"  发布结果: success={result.success}, notified={result.subscribers_notified}")
        
        if not result.success:
            print(f"  ✗ 发布失败: {result.errors}")
        
        # 等待一下，让输出更清晰
        time.sleep(0.5)
    
    # 取消订阅
    print_separator("清理")
    success = broker.unsubscribe("direction_result", subscription_id)
    print(f"✓ 取消订阅: {success}")


async def test_current_mappings():
    """测试查询当前所有摄像头映射"""
    print_separator("查询当前摄像头映射")
    
    # 初始化
    broker, camera_mapper = await initialize_broker()
    
    # 获取所有方向映射
    direction_mappings = camera_mapper.get_all_direction_mappings()
    
    print(f"\n当前配置的方向数量: {len(direction_mappings)}")
    
    for direction, cameras in direction_mappings.items():
        print(f"\n方向: {direction}")
        print(f"  摄像头数量: {len(cameras)}")
        
        for camera in cameras:
            print(f"    - {camera['name']} ({camera['id']})")
            print(f"      URL: {camera['url']}")
            print(f"      状态: {camera['status']}")
    
    # 获取所有角度范围
    angle_ranges = camera_mapper.get_all_angle_ranges()
    
    print(f"\n当前配置的角度范围数量: {len(angle_ranges)}")
    
    for angle_range in angle_ranges:
        print(f"\n角度范围: {angle_range['min_angle']}° - {angle_range['max_angle']}°")
        print(f"  摄像头数量: {len(angle_range['cameras'])}")
        
        for camera in angle_range['cameras']:
            print(f"    - {camera['name']} ({camera['id']})")
            print(f"      URL: {camera['url']}")


async def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("  Broker 方向订阅测试 - 摄像头 URL 输出")
    print("=" * 60)
    
    try:
        # 测试 1: 查询当前映射
        await test_current_mappings()
        
        # 等待一下
        time.sleep(1)
        
        # 测试 2: 订阅和消息发布
        await test_direction_subscription()
        
        print_separator("测试完成")
        print("✓ 所有测试通过!")
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main())
