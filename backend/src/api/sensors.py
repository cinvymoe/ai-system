"""
Sensor API endpoints

提供传感器数据的WebSocket流和运动模式控制端点。
"""

import asyncio
import json
import logging
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
try:
    from collectors.sensors.mock_sensor import MockSensorDevice
    from collectors.processors.motion_processor import MotionDirectionProcessor
except ImportError:
    from src.collectors.sensors.mock_sensor import MockSensorDevice
    from src.collectors.processors.motion_processor import MotionDirectionProcessor


# 配置日志
logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/api/sensor", tags=["sensors"])

# 全局传感器设备实例
_sensor_device: Optional[MockSensorDevice] = None
_sensor_lock = asyncio.Lock()


@router.websocket("/stream")
async def sensor_stream_websocket(websocket: WebSocket):
    """
    WebSocket端点，推送实时传感器数据和运动指令
    
    连接后自动开始推送数据流，包括：
    - sensor_data: 原始传感器数据（加速度、角速度、角度等）
    - motion_command: 处理后的运动指令
    
    消息格式：
    {
        "type": "sensor_data" | "motion_command" | "error",
        "timestamp": "ISO格式时间戳",
        "data": { ... }
    }
    """
    global _sensor_device
    
    logger.info(f"WebSocket连接请求 - Client: {websocket.client}")
    try:
        await websocket.accept()
        logger.info("✓ WebSocket客户端已连接并接受")
    except Exception as e:
        logger.error(f"✗ WebSocket接受失败: {e}")
        raise
    
    # 创建MockSensorDevice和MotionDirectionProcessor
    sensor_device = None
    processor = None
    
    try:
        # 使用锁保护全局传感器设备的创建
        async with _sensor_lock:
            if _sensor_device is None:
                _sensor_device = MockSensorDevice(
                    sensor_id="mock_sensor_ws",
                    motion_pattern="sequence",  # 自动按序列切换运动模式
                    config={
                        'interval': 0.1,  # 10Hz
                        'noise_level': 0.01,
                    }
                )
                await _sensor_device.connect()
                logger.info("MockSensorDevice已创建并连接")
            
            sensor_device = _sensor_device
        
        # 创建运动方向处理器
        processor = MotionDirectionProcessor(config={
            'motion_threshold': 0.005,
            'angular_threshold': 2.0,
            'direction_threshold': 0.002,
            'rotation_threshold': 5.0,
            'velocity_threshold': 0.0005,
        })
        logger.info("MotionDirectionProcessor已创建")
        
        # 订阅数据流
        async for collected_data in sensor_device.collect_stream():
            try:
                # 解析传感器数据
                raw_data_str = collected_data.raw_data.decode('utf-8')
                logger.debug(f"收到原始数据: {raw_data_str[:100]}...")  # 只记录前100个字符
                sensor_data = json.loads(raw_data_str)
                
                # 发送传感器数据消息
                sensor_message = {
                    "type": "sensor_data",
                    "timestamp": collected_data.timestamp.isoformat(),
                    "data": {
                        "acceleration": {
                            "x": sensor_data.get('加速度X(g)', 0.0),
                            "y": sensor_data.get('加速度Y(g)', 0.0),
                            "z": sensor_data.get('加速度Z(g)', 0.0),
                        },
                        "angularVelocity": {
                            "x": sensor_data.get('角速度X(°/s)', 0.0),
                            "y": sensor_data.get('角速度Y(°/s)', 0.0),
                            "z": sensor_data.get('角速度Z(°/s)', 0.0),
                        },
                        "angles": {
                            "x": sensor_data.get('角度X(°)', 0.0),
                            "y": sensor_data.get('角度Y(°)', 0.0),
                            "z": sensor_data.get('角度Z(°)', 0.0),
                        },
                        "temperature": sensor_data.get('温度(°C)', 25.0),
                        "battery": sensor_data.get('电量(%)', 100.0),
                    }
                }
                await websocket.send_json(sensor_message)
                
                # 处理数据生成运动指令
                motion_command = processor.process(sensor_data)
                
                # 发送运动指令消息
                motion_message = {
                    "type": "motion_command",
                    "timestamp": motion_command.timestamp.isoformat(),
                    "data": {
                        "command": motion_command.command,
                        "intensity": float(motion_command.intensity),
                        "angularIntensity": float(motion_command.angular_intensity),
                        "rawDirection": str(motion_command.raw_direction),
                        "isMotionStart": bool(motion_command.is_motion_start),
                    }
                }
                await websocket.send_json(motion_message)
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析错误: {e}")
                logger.error(f"原始数据: {collected_data.raw_data}")
                try:
                    error_message = {
                        "type": "error",
                        "timestamp": collected_data.timestamp.isoformat(),
                        "data": {
                            "error": f"数据解析失败: {str(e)}",
                            "raw_data": collected_data.raw_data.decode('utf-8', errors='replace')[:200]
                        }
                    }
                    await websocket.send_json(error_message)
                except (WebSocketDisconnect, RuntimeError):
                    # Client disconnected, stop processing
                    break
                
            except WebSocketDisconnect:
                # Client disconnected during processing
                logger.info("WebSocket客户端在数据处理时断开连接")
                break
                
            except Exception as e:
                logger.error(f"数据处理错误: {e}", exc_info=True)
                try:
                    error_message = {
                        "type": "error",
                        "timestamp": collected_data.timestamp.isoformat(),
                        "data": {
                            "error": f"处理错误: {str(e)}"
                        }
                    }
                    await websocket.send_json(error_message)
                except (WebSocketDisconnect, RuntimeError):
                    # Client disconnected, stop processing
                    break
    
    except WebSocketDisconnect:
        logger.info("WebSocket客户端已断开连接")
    
    except Exception as e:
        logger.error(f"WebSocket错误: {e}", exc_info=True)
    
    finally:
        # 清理资源（保持传感器设备运行以支持多个客户端）
        logger.info("WebSocket连接已关闭")
