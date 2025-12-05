#!/usr/bin/env python3
"""测试WebSocket连接"""

import asyncio
import json
from datetime import datetime

try:
    import websockets
except ImportError:
    print("需要安装websockets: pip install websockets")
    exit(1)


async def test_websocket():
    """测试WebSocket连接 - 持续监听"""
    uri = "ws://127.0.0.1:8000/api/sensor/stream"
    
    print(f"连接到 {uri}...")
    print("按 Ctrl+C 停止监听\n")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✓ WebSocket连接成功!")
            print("-" * 80)
            
            message_count = 0
            last_motion_command = None
            
            # 持续接收消息
            while True:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                    data = json.loads(message)
                    message_count += 1
                    
                    msg_type = data.get('type')
                    timestamp = data.get('timestamp', '')
                    
                    if msg_type == 'sensor_data':
                        # 只显示传感器数据的简要信息
                        acc = data['data']['acceleration']
                        gyro = data['data']['angularVelocity']
                        angles = data['data']['angles']
                        
                        print(f"[{message_count:04d}] 传感器数据 | {timestamp[-12:]}")
                        print(f"  加速度: X={acc['x']:7.3f} Y={acc['y']:7.3f} Z={acc['z']:7.3f} g")
                        print(f"  角速度: X={gyro['x']:7.2f} Y={gyro['y']:7.2f} Z={gyro['z']:7.2f} °/s")
                        print(f"  角度:   X={angles['x']:7.2f} Y={angles['y']:7.2f} Z={angles['z']:7.2f} °")
                        
                    elif msg_type == 'motion_command':
                        cmd = data['data']
                        command = cmd['command']
                        intensity = cmd['intensity']
                        angular_intensity = cmd['angularIntensity']
                        is_motion_start = cmd.get('isMotionStart', False)
                        direction = cmd.get('direction', {})
                        
                        # 只在运动指令变化时显示
                        if command != last_motion_command or is_motion_start:
                            print(f"\n{'='*80}")
                            print(f"[{message_count:04d}] 运动指令 | {timestamp[-12:]}")
                            print(f"  指令: {command:12s} | 线性强度: {intensity:.4f} | 角度强度: {angular_intensity:.4f}")
                            
                            # 打印运动方向信息
                            if direction:
                                print(f"  运动方向:")
                                print(f"    前后: {direction.get('forward', 0):7.3f} (正=前进, 负=后退)")
                                print(f"    左右: {direction.get('lateral', 0):7.3f} (正=右移, 负=左移)")
                                print(f"    旋转: {direction.get('rotation', 0):7.3f} (正=右转, 负=左转)")
                            
                            if is_motion_start:
                                print(f"  >>> 运动开始 <<<")
                            print(f"{'='*80}\n")
                            last_motion_command = command
                        
                    elif msg_type == 'error':
                        error_msg = data['data'].get('error', 'Unknown error')
                        print(f"\n✗ 错误消息: {error_msg}\n")
                    
                except asyncio.TimeoutError:
                    print("✗ 30秒内未收到消息，连接可能已断开")
                    break
                except json.JSONDecodeError as e:
                    print(f"✗ JSON解析错误: {e}")
                except KeyboardInterrupt:
                    print("\n\n用户中断，正在关闭连接...")
                    break
                    
    except ConnectionRefusedError:
        print("✗ 连接被拒绝 - 确保后端正在运行")
    except KeyboardInterrupt:
        print("\n\n用户中断")
    except Exception as e:
        print(f"✗ 错误: {type(e).__name__}: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(test_websocket())
    except KeyboardInterrupt:
        print("\n程序已退出")
