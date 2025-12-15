#!/usr/bin/env python3
"""
测试 JY901 传感器 WebSocket 数据流

连接到传感器 WebSocket 端点并接收实时数据
"""

import asyncio
import json
import websockets
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_websocket_connection():
    """测试 WebSocket 连接和数据接收"""
    uri = "ws://localhost:8000/api/sensor/stream"
    
    logger.info(f"连接到 WebSocket: {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            logger.info("✓ WebSocket 连接成功")
            
            message_count = 0
            sensor_data_count = 0
            motion_command_count = 0
            error_count = 0
            
            # 接收消息
            async for message in websocket:
                try:
                    data = json.loads(message)
                    message_count += 1
                    
                    msg_type = data.get('type', 'unknown')
                    timestamp = data.get('timestamp', '')
                    
                    if msg_type == 'sensor_data':
                        sensor_data_count += 1
                        sensor_info = data.get('data', {})
                        
                        acc = sensor_info.get('acceleration', {})
                        gyro = sensor_info.get('angularVelocity', {})
                        angles = sensor_info.get('angles', {})
                        temp = sensor_info.get('temperature', 0)
                        battery = sensor_info.get('battery', 0)
                        
                        logger.info(
                            f"[{sensor_data_count:3d}] 传感器数据 - "
                            f"加速度: ({acc.get('x', 0):.3f}, {acc.get('y', 0):.3f}, {acc.get('z', 0):.3f}) "
                            f"角速度: ({gyro.get('x', 0):.2f}, {gyro.get('y', 0):.2f}, {gyro.get('z', 0):.2f}) "
                            f"角度: ({angles.get('x', 0):.1f}, {angles.get('y', 0):.1f}, {angles.get('z', 0):.1f}) "
                            f"温度: {temp:.1f}°C 电量: {battery:.0f}%"
                        )
                    
                    elif msg_type == 'motion_command':
                        motion_command_count += 1
                        motion_info = data.get('data', {})
                        
                        command = motion_info.get('command', 'unknown')
                        intensity = motion_info.get('intensity', 0)
                        angular_intensity = motion_info.get('angularIntensity', 0)
                        is_motion_start = motion_info.get('isMotionStart', False)
                        raw_direction = motion_info.get('rawDirection', '')
                        
                        logger.info(
                            f"[{motion_command_count:3d}] 运动指令 - "
                            f"命令: {command}, 强度: {intensity:.4f}, "
                            f"角强度: {angular_intensity:.4f}, "
                            f"运动开始: {is_motion_start}, 原始方向: {raw_direction}"
                        )
                    
                    elif msg_type == 'error':
                        error_count += 1
                        error_info = data.get('data', {})
                        error_msg = error_info.get('error', 'Unknown error')
                        
                        logger.error(f"[{error_count:3d}] 错误消息: {error_msg}")
                        
                        # 如果有可用字段信息，显示它们
                        if 'available_fields' in error_info:
                            logger.info(f"可用字段: {error_info['available_fields']}")
                    
                    else:
                        logger.warning(f"未知消息类型: {msg_type}")
                    
                    # 限制测试消息数量
                    if message_count >= 50:
                        logger.info(f"已接收 {message_count} 条消息，测试完成")
                        break
                        
                except json.JSONDecodeError as e:
                    logger.error(f"JSON 解析错误: {e}")
                    logger.error(f"原始消息: {message}")
                
                except KeyboardInterrupt:
                    logger.info("用户中断测试")
                    break
                
                except Exception as e:
                    logger.error(f"处理消息时发生错误: {e}")
            
            # 显示统计信息
            logger.info("=" * 60)
            logger.info("测试统计:")
            logger.info(f"总消息数: {message_count}")
            logger.info(f"传感器数据: {sensor_data_count}")
            logger.info(f"运动指令: {motion_command_count}")
            logger.info(f"错误消息: {error_count}")
            logger.info("=" * 60)
    
    except websockets.exceptions.ConnectionClosed as e:
        logger.error(f"WebSocket 连接关闭: {e}")
    
    except websockets.exceptions.InvalidURI as e:
        logger.error(f"无效的 WebSocket URI: {e}")
    
    except ConnectionRefusedError:
        logger.error("连接被拒绝，请确保后端服务正在运行")
        logger.info("启动后端服务: cd backend && python -m uvicorn src.main:app --reload")
    
    except Exception as e:
        logger.error(f"WebSocket 测试失败: {e}")


async def test_sensor_direct():
    """直接测试 JY901 传感器"""
    logger.info("直接测试 JY901 传感器...")
    
    try:
        from src.collectors.sensors.jy901 import JY901Sensor
        
        sensor = JY901Sensor(
            sensor_id="direct_test",
            config={
                'mode': 'realtime',
                'port': '/dev/ttyACM0',
                'baudrate': 9600,
                'timeout': 1.0,
            }
        )
        
        logger.info("连接传感器...")
        if await sensor.connect():
            logger.info("✓ 传感器连接成功")
            
            # 等待数据准备
            await asyncio.sleep(2)
            
            # 读取几条数据
            for i in range(5):
                try:
                    data = await sensor.read_sensor_data()
                    logger.info(f"[{i+1}] 传感器数据字段: {list(data.keys())}")
                    
                    # 显示关键数据
                    if '加速度X(g)' in data:
                        logger.info(f"    加速度: X={data.get('加速度X(g)', 0):.3f}g")
                    if '温度(°C)' in data:
                        logger.info(f"    温度: {data.get('温度(°C)', 0):.1f}°C")
                    
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"读取数据失败: {e}")
            
            await sensor.disconnect()
            logger.info("✓ 传感器已断开")
        
        else:
            logger.error("❌ 传感器连接失败")
    
    except ImportError as e:
        logger.error(f"导入传感器模块失败: {e}")
    except Exception as e:
        logger.error(f"直接传感器测试失败: {e}")


async def main():
    """主函数"""
    logger.info("JY901 传感器 WebSocket 测试")
    logger.info("=" * 60)
    
    # 选择测试模式
    print("选择测试模式:")
    print("1. WebSocket 连接测试")
    print("2. 直接传感器测试")
    print("3. 两者都测试")
    
    choice = input("请输入选择 (1-3): ").strip()
    
    if choice == '1':
        await test_websocket_connection()
    elif choice == '2':
        await test_sensor_direct()
    elif choice == '3':
        await test_sensor_direct()
        print("\n" + "=" * 60)
        await test_websocket_connection()
    else:
        logger.error("无效选择")
        return
    
    logger.info("测试完成")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n测试被用户中断")
    except Exception as e:
        logger.error(f"测试程序错误: {e}")