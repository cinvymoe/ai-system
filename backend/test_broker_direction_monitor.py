"""
Broker 方向订阅实时监控

持续监听方向消息并实时输出摄像头 URL
按 Ctrl+C 退出
"""

import sys
import asyncio
import signal
from datetime import datetime

# Add src to path
sys.path.insert(0, 'src')

from broker.broker import MessageBroker
from broker.handlers import DirectionMessageHandler
from broker.models import MessageData
from broker.mapper import CameraMapper
from database import get_db


# 全局标志，用于优雅退出
running = True


def signal_handler(sig, frame):
    """处理 Ctrl+C 信号"""
    global running
    print("\n\n正在退出...")
    running = False


async def main():
    """主函数"""
    global running
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    
    print("=" * 70)
    print("  Broker 方向订阅实时监控")
    print("=" * 70)
    print("\n初始化中...")
    
    try:
        # 获取消息代理实例
        broker = MessageBroker.get_instance()
        
        # 设置摄像头映射器
        camera_mapper = CameraMapper(db_session_factory=get_db)
        broker.set_camera_mapper(camera_mapper)
        
        # 注册方向消息处理器（如果还没注册）
        if "direction_result" not in broker.get_registered_types():
            broker.register_message_type("direction_result", DirectionMessageHandler())
        
        print("✓ 消息代理初始化完成")
        
        # 创建回调函数
        def direction_callback(message: MessageData):
            """处理方向消息"""
            direction = message.data.get("command", "未知")
            intensity = message.data.get("intensity", 0)
            
            print("\n" + "-" * 70)
            print(f"⚡ 收到方向消息: {direction.upper()}")
            print(f"   时间: {message.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   强度: {intensity}")
            
            # 获取对应的摄像头
            try:
                cameras = camera_mapper.get_cameras_by_direction(direction)
                
                if cameras:
                    print(f"\n   📹 关联摄像头 ({len(cameras)} 个):")
                    for i, camera in enumerate(cameras, 1):
                        status_icon = "🟢" if camera.status == "online" else "🔴"
                        print(f"      {i}. {status_icon} {camera.name}")
                        print(f"         ID:  {camera.id}")
                        print(f"         URL: {camera.url}")
                else:
                    print(f"\n   ℹ️  该方向没有关联的摄像头")
                    
            except Exception as e:
                print(f"\n   ❌ 获取摄像头信息失败: {e}")
            
            print("-" * 70)
        
        # 订阅方向消息
        subscription_id = broker.subscribe("direction_result", direction_callback)
        
        print(f"✓ 已订阅 direction_result 消息")
        print(f"  订阅 ID: {subscription_id}")
        
        # 显示当前配置
        print("\n" + "=" * 70)
        print("  当前摄像头配置")
        print("=" * 70)
        
        direction_mappings = camera_mapper.get_all_direction_mappings()
        
        for direction, cameras in direction_mappings.items():
            if cameras:
                print(f"\n{direction}:")
                for camera in cameras:
                    status_icon = "🟢" if camera['status'] == "online" else "🔴"
                    print(f"  {status_icon} {camera['name']}: {camera['url']}")
        
        print("\n" + "=" * 70)
        print("  正在监听方向消息... (按 Ctrl+C 退出)")
        print("=" * 70)
        
        # 保持运行，等待消息
        while running:
            await asyncio.sleep(0.1)
        
        # 取消订阅
        broker.unsubscribe("direction_result", subscription_id)
        print("\n✓ 已取消订阅")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
