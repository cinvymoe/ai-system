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
    from collectors.sensors.jy901 import JY901Sensor
    from collectors.processors.motion_processor import MotionDirectionProcessor
    from broker.broker import MessageBroker
except ImportError:
    from src.collectors.sensors.jy901 import JY901Sensor
    from src.collectors.processors.motion_processor import MotionDirectionProcessor
    from src.broker.broker import MessageBroker


# 配置日志
logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/api/sensor", tags=["sensors"])

# 全局传感器设备实例
_sensor_device: Optional[JY901Sensor] = None
_sensor_lock = asyncio.Lock()


@router.websocket("/stream")
async def sensor_stream_websocket(websocket: WebSocket):
    """
    WebSocket端点，推送实时JY901传感器数据和运动指令
    
    连接后自动开始推送数据流，包括：
    - sensor_data: JY901九轴传感器数据（加速度、角速度、角度、温度、电量等）
    - motion_command: 处理后的运动指令
    
    消息格式：
    {
        "type": "sensor_data" | "motion_command" | "error",
        "timestamp": "ISO格式时间戳",
        "data": { ... }
    }
    
    JY901传感器通过串口 /dev/ttyACM0 连接，波特率 9600
    """
    global _sensor_device
    
    logger.info(f"WebSocket连接请求 - Client: {websocket.client}")
    try:
        await websocket.accept()
        logger.info("✓ WebSocket客户端已连接并接受")
    except Exception as e:
        logger.error(f"✗ WebSocket接受失败: {e}")
        raise
    
    # 创建JY901Sensor和MotionDirectionProcessor
    sensor_device = None
    processor = None
    
    try:
        # 使用锁保护全局传感器设备的创建
        async with _sensor_lock:
            if _sensor_device is None:
                _sensor_device = JY901Sensor(
                    sensor_id="jy901_sensor_ws",
                    config={
                        'mode': 'realtime',  # 使用实时模式
                        'port': '/dev/ttyACM0',  # JY901传感器串口
                        'baudrate': 9600,
                        'timeout': 1.0,
                    }
                )
                await _sensor_device.connect()
                logger.info("JY901Sensor已创建并连接")
            
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
        
        # 等待传感器初始化和数据准备
        logger.info("等待JY901传感器数据准备...")
        await asyncio.sleep(2)  # 给传感器2秒时间准备数据
        
        # 订阅数据流
        async for collected_data in sensor_device.collect_stream():
            try:
                # 从JY901传感器获取数据
                # JY901传感器的数据在metadata['data']中
                sensor_data = collected_data.metadata.get('data', {})
                logger.debug(f"收到JY901传感器数据: {list(sensor_data.keys())}")  # 记录数据字段
                
                # 检查是否有必需的传感器数据
                if not sensor_data:
                    logger.warning("传感器数据为空，等待数据...")
                    await asyncio.sleep(0.1)  # 短暂等待
                    continue
                
                # 检查必需字段是否存在
                required_fields = ['加速度X(g)', '加速度Y(g)', '加速度Z(g)']
                missing_fields = [field for field in required_fields if field not in sensor_data]
                if missing_fields:
                    logger.warning(f"传感器数据缺少字段: {missing_fields}，当前字段: {list(sensor_data.keys())}")
                    await asyncio.sleep(0.1)  # 短暂等待
                    continue
                
                logger.debug(f"处理完整的传感器数据: {sensor_data}")
                
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
                
                # 发布角度消息到消息代理
                # Requirements 3.1, 3.3: 发布角度值数据供其他模块订阅
                try:
                    broker = MessageBroker.get_instance()
                    angle_z = sensor_data.get('角度Z(°)', 0.0)
                    
                    # 发布角度消息，格式符合 AngleMessageHandler 要求
                    broker.publish("angle_value", {
                        "angle": float(angle_z),
                        "timestamp": collected_data.timestamp.isoformat()
                    })
                    
                    logger.debug(f"Published angle message: {angle_z}°")
                    
                except Exception as broker_error:
                    # 消息代理错误不应影响 WebSocket 数据流
                    logger.error(f"Failed to publish angle message to broker: {broker_error}")
                    # 继续处理，不中断 WebSocket 流
                
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
                
            except KeyError as e:
                logger.error(f"传感器数据字段缺失: {e}")
                logger.error(f"可用字段: {list(sensor_data.keys())}")
                try:
                    error_message = {
                        "type": "error",
                        "timestamp": collected_data.timestamp.isoformat(),
                        "data": {
                            "error": f"传感器数据字段缺失: {str(e)}",
                            "available_fields": list(sensor_data.keys())
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


@router.post("/stop")
async def stop_sensor():
    """
    停止传感器数据采集，关闭串口连接
    
    用于在离开传感器设置页面时清理资源
    """
    global _sensor_device
    
    try:
        async with _sensor_lock:
            if _sensor_device is not None:
                logger.info("正在停止传感器设备...")
                await _sensor_device.disconnect()
                _sensor_device = None
                logger.info("✓ 传感器设备已停止，串口已关闭")
                return {"status": "success", "message": "传感器已停止"}
            else:
                logger.info("传感器设备未运行")
                return {"status": "success", "message": "传感器未运行"}
    except Exception as e:
        logger.error(f"✗ 停止传感器失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"停止传感器失败: {str(e)}")
