"""
通过 Sensor Stream WebSocket 获取方向并输出摄像头 URL

功能：
1. 连接到 /api/sensor/stream WebSocket
2. 接收实时传感器数据和运动指令
3. 当收到方向指令时，查询并输出对应的摄像头 URL
4. 同时订阅 broker 的 direction_result 消息
"""

import sys
import asyncio
import signal
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, 'src')

import websockets

try:
    from broker.broker import MessageBroker
    from broker.handlers import DirectionMessageHandler
    from broker.models import MessageData
    from broker.mapper import CameraMapper
    from database import get_db
except ImportError:
    from src.broker.broker import MessageBroker
    from src.broker.handlers import DirectionMessageHandler
    from src.broker.models import MessageData
    from src.broker.mapper import CameraMapper
    from src.database import get_db


# 全局标志
running = True


def signal_handler(sig, frame):
    """处理 Ctrl+C 信号"""
    global running
    print("\n\n正在退出...")
    running = False


async def initialize_broker():
    """初始化消息代理"""
    print("初始化消息代理...")
    
    # 获取消息代理实例
    broker = MessageBroker.get_instance()
    
    # 设置摄像头映射器
    camera_mapper = CameraMapper(db_session_factory=get_db)
    broker.set_camera_mapper(camera_mapper)
    
    # 注册方向消息处理器（如果还没注册）
    if "direction_result" not in broker.get_registered_types():
        broker.register_message_type("direction_result", DirectionMessageHandler())
    
    print("✓ 消息代理初始化完成")
    
    return broker, camera_mapper


def print_cameras(direction: str, camera_mapper: CameraMapper):
    """打印指定方向的摄像头信息"""
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


async def connect_sensor_stream(camera_mapper: CameraMapper):
    """连接到传感器 WebSocket 流"""
    global running
    
    # WebSocket URL
    ws_url = "ws://localhost:8000/api/sensor/stream"
    
    print(f"\n正在连接到传感器 WebSocket: {ws_url}")
    
    try:
        async with websockets.connect(ws_url) as websocket:
            print("✓ 已连接到传感器 WebSocket")
            print("\n" + "=" * 70)
            print("  正在接收传感器数据和运动指令...")
            print("=" * 70)
            
            last_direction = None
            
            while running:
                try:
                    # 接收消息
                    message = await asyncio.wait_for(
                        websocket.recv(),
                        timeout=1.0
                    )
                    
                    # 解析消息
                    data = json.loads(message)
                    msg_type = data.get("type")
                    timestamp = data.get("timestamp")
                    msg_data = data.get("data", {})
                    
                    if msg_type == "sensor_data":
                        # 传感器数据 - 简单显示
                        angles = msg_data.get("angles", {})
                        print(f"\r传感器角度: X={angles.get('x', 0):.1f}° "
                              f"Y={angles.get('y', 0):.1f}° "
                              f"Z={angles.get('z', 0):.1f}°", end="", flush=True)
                    
                    elif msg_type == "motion_command":
                        # 运动指令 - 显示方向和摄像头
                        direction = msg_data.get("command")
                        intensity = msg_data.get("intensity", 0)
                        angular_intensity = msg_data.get("angularIntensity", 0)
                        is_motion_start = msg_data.get("isMotionStart", False)
                        
                        # 只在方向改变或运动开始时显示
                        if direction != last_direction or is_motion_start:
                            print()  # 换行
                            print("\n" + "-" * 70)
                            print(f"⚡ 运动指令: {direction.upper()}")
                            print(f"   时间: {timestamp}")
                            print(f"   强度: {intensity:.3f}")
                            print(f"   角度强度: {angular_intensity:.3f}")
                            if is_motion_start:
                                print(f"   🚀 运动开始")
                            
                            # 显示对应的摄像头
                            print_cameras(direction, camera_mapper)
                            print("-" * 70)
                            
                            last_direction = direction
                    
                    elif msg_type == "error":
                        # 错误消息
                        error = msg_data.get("error")
                        print(f"\n❌ 错误: {error}")
                
                except asyncio.TimeoutError:
                    # 超时是正常的，继续等待
                    continue
                
                except json.JSONDecodeError as e:
                    print(f"\n❌ JSON 解析错误: {e}")
                
                except Exception as e:
                    print(f"\n❌ 处理消息时出错: {e}")
                    import traceback
                    traceback.print_exc()
    
    except websockets.exceptions.WebSocketException as e:
        print(f"\n❌ WebSocket 连接错误: {e}")
        print("\n提示: 请确保后端服务正在运行 (python -m uvicorn src.main:app)")
    
    except Exception as e:
        print(f"\n❌ 连接失败: {e}")
        import traceback
        traceback.print_exc()


async def subscribe_broker_messages(camera_mapper: CameraMapper):
    """订阅 broker 的方向消息（可选，用于验证）"""
    global running
    
    broker = MessageBroker.get_instance()
    
    def direction_callback(message: MessageData):
        """处理 broker 的方向消息"""
        direction = message.data.get("command", "未知")
        print(f"\n[Broker] 收到方向消息: {direction}")
    
    # 订阅
    subscription_id = broker.subscribe("direction_result", direction_callback)
    print(f"✓ 已订阅 broker direction_result 消息 (ID: {subscription_id})")
    
    try:
        # 保持订阅活跃
        while running:
            await asyncio.sleep(0.1)
    finally:
        # 取消订阅
        broker.unsubscribe("direction_result", subscription_id)
        print("\n✓ 已取消 broker 订阅")


async def main():
    """主函数"""
    global running
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    
    print("=" * 70)
    print("  传感器方向 → 摄像头 URL 实时监控")
    print("=" * 70)
    
    try:
        # 初始化 broker 和 camera mapper
        broker, camera_mapper = await initialize_broker()
        
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
        
        # 创建任务
        tasks = [
            asyncio.create_task(connect_sensor_stream(camera_mapper)),
            # 可选：同时订阅 broker 消息
            # asyncio.create_task(subscribe_broker_messages(camera_mapper)),
        ]
        
        # 等待任务完成
        await asyncio.gather(*tasks, return_exceptions=True)
        
        print("\n✓ 程序已退出")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
