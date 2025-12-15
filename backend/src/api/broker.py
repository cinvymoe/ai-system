"""
Broker API endpoints

提供消息代理的WebSocket流和HTTP查询端点。
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException

try:
    from broker.broker import MessageBroker
    from broker.models import MessageData, CameraInfo
    from broker.mapper import CameraMapper
    from broker.handlers import DirectionMessageHandler, AngleMessageHandler, AIAlertMessageHandler
    from broker.data_manager import DataManager, ManagedMessage
    from database import get_db
    from collectors.sensors.jy901 import JY901Sensor
    from collectors.processors.motion_processor import MotionDirectionProcessor
except ImportError:
    from src.broker.broker import MessageBroker
    from src.broker.models import MessageData, CameraInfo
    from src.broker.mapper import CameraMapper
    from src.broker.handlers import DirectionMessageHandler, AngleMessageHandler, AIAlertMessageHandler
    from src.broker.data_manager import DataManager, ManagedMessage
    from src.database import get_db
    from src.collectors.sensors.jy901 import JY901Sensor
    from src.collectors.processors.motion_processor import MotionDirectionProcessor

# 配置日志
logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/api/broker", tags=["broker"])

# 活跃的 WebSocket 连接计数（用于统计）
_active_connections = 0
_connections_lock = asyncio.Lock()

# 消息代理初始化标志
_broker_initialized = False
_init_lock = asyncio.Lock()

# 全局 DataManager 实例
_data_manager: Optional[DataManager] = None

# 全局传感器设备实例
_sensor_device: Optional[JY901Sensor] = None
_sensor_lock = asyncio.Lock()
_sensor_task: Optional[asyncio.Task] = None
_sensor_running = False


async def _initialize_broker():
    """
    初始化消息代理和处理器
    
    注意：此函数现在只是一个薄包装层，实际初始化逻辑已移至 MessageBroker.initialize_handlers()
    """
    global _broker_initialized, _data_manager
    
    async with _init_lock:
        if _broker_initialized:
            return
        
        try:
            # 获取消息代理实例
            broker = MessageBroker.get_instance()
            
            # 创建摄像头映射器
            camera_mapper = CameraMapper(db_session_factory=get_db)
            
            # 使用 MessageBroker 的 initialize_handlers 方法进行初始化
            # 这将设置映射器并注册默认的消息处理器
            # broker.initialize_handlers(camera_mapper)
            
            # 初始化 DataManager
            _data_manager = DataManager(camera_getter=_get_cameras_for_message)
            await _data_manager.initialize()
            
            # 注意：不再在全局注册广播回调
            # 每个 WebSocket 连接会独立订阅消息类型或使用 DataManager
            
            _broker_initialized = True
            logger.info("Message broker and DataManager initialized for WebSocket API")
            
        except Exception as e:
            logger.error(f"Failed to initialize message broker: {e}", exc_info=True)
            raise





def _make_serializable(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    确保字典中的所有值都是 JSON 可序列化的
    
    Args:
        data: 原始数据字典
        
    Returns:
        Dict[str, Any]: 可序列化的数据字典
    """
    serializable_data = {}
    for key, value in data.items():
        if isinstance(value, (str, int, float, bool, type(None))):
            serializable_data[key] = value
        elif isinstance(value, datetime):
            serializable_data[key] = value.isoformat()
        elif isinstance(value, (list, tuple)):
            serializable_data[key] = [
                item.isoformat() if isinstance(item, datetime) else item
                for item in value
            ]
        elif isinstance(value, dict):
            serializable_data[key] = _make_serializable(value)
        else:
            serializable_data[key] = str(value)
    
    return serializable_data


async def _get_cameras_for_message(message: MessageData) -> List[CameraInfo]:
    """根据消息获取对应的摄像头列表"""
    try:
        broker = MessageBroker.get_instance()
        camera_mapper = broker._camera_mapper
        
        if not camera_mapper:
            logger.warning("Camera mapper not set in broker")
            return []
        
        if message.type == "direction_result":
            direction = message.data.get("command")
            if direction:
                return camera_mapper.get_cameras_by_direction(direction)
        
        elif message.type == "angle_value":
            angle = message.data.get("angle")
            if angle is not None:
                return camera_mapper.get_cameras_by_angle(float(angle))
        
        elif message.type == "ai_alert":
            return camera_mapper.get_cameras_by_ai_alert(message.data)
        
        return []
        
    except Exception as e:
        logger.error(f"Error getting cameras for message {message.message_id}: {e}")
        return []


async def _get_cameras_details(camera_ids: List[str]) -> List[Dict[str, Any]]:
    """
    根据摄像头 ID 列表获取完整的摄像头信息
    
    Args:
        camera_ids: 摄像头 ID 列表
        
    Returns:
        List[Dict]: 包含 id, name, url, status, directions 的摄像头信息列表
    """
    try:
        # 导入 Camera 模型
        try:
            from models.camera import Camera
        except ImportError:
            from src.models.camera import Camera
        
        # 获取数据库会话
        db = next(get_db())
        
        try:
            # 查询摄像头信息
            cameras = db.query(Camera).filter(Camera.id.in_(camera_ids)).all()
            
            # 转换为字典列表
            cameras_info = []
            for camera in cameras:
                cameras_info.append({
                    "id": camera.id,
                    "name": camera.name,
                    "url": camera.url,
                    "status": camera.status,
                    "directions": camera.directions or []
                })
            
            return cameras_info
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error getting camera details: {e}", exc_info=True)
        # 降级处理：返回只包含 ID 的列表
        return [{"id": camera_id} for camera_id in camera_ids]


async def _start_sensor_stream():
    """启动传感器数据流，自动发布到 MessageBroker"""
    global _sensor_device, _sensor_running
    
    try:
        # 使用锁保护全局传感器设备的创建
        async with _sensor_lock:
            if _sensor_device is None:
                _sensor_device = JY901Sensor(
                    sensor_id="jy901_sensor_broker",
                    config={
                        'mode': 'realtime',
                        'port': '/dev/ttyACM0',
                        'baudrate': 9600,
                        'timeout': 1.0,
                    }
                )
                await _sensor_device.connect()
                logger.info("JY901 传感器已创建并连接（用于 broker）")
        
        _sensor_running = True
        logger.info("传感器数据流已启动")
        
        # 等待传感器初始化
        await asyncio.sleep(2)
        
        # 获取 MessageBroker 实例
        broker = MessageBroker.get_instance()
        
        # 创建运动方向处理器
        processor = MotionDirectionProcessor(config={
            'motion_threshold': 0.005,
            'angular_threshold': 2.0,
            'direction_threshold': 0.002,
            'rotation_threshold': 5.0,
            'velocity_threshold': 0.0005,
        })
        
        # 持续采集并发布数据
        async for collected_data in _sensor_device.collect_stream():
            if not _sensor_running:
                logger.info("传感器数据流停止标志已设置，退出循环")
                break
            
            try:
                sensor_data = collected_data.metadata.get('data', {})
                
                if not sensor_data:
                    await asyncio.sleep(0.1)
                    continue
                
                # 检查必需字段
                required_fields = ['加速度X(g)', '加速度Y(g)', '加速度Z(g)']
                if not all(field in sensor_data for field in required_fields):
                    await asyncio.sleep(0.1)
                    continue
                
                # 发布角度消息到 MessageBroker
                angle_z = sensor_data.get('角度Z(°)', 0.0)
                broker.publish("angle_value", {
                    "angle": float(angle_z),
                    "timestamp": collected_data.timestamp.isoformat()
                })
                
                # 处理运动指令并发布
                motion_command = processor.process(sensor_data)
                if motion_command.command != "idle":
                    broker.publish("direction_result", {
                        "command": motion_command.command,
                        "intensity": float(motion_command.intensity),
                        "timestamp": motion_command.timestamp.isoformat()
                    })
                
                logger.debug(f"发布传感器数据: 角度={angle_z}°, 指令={motion_command.command}")
                
            except Exception as e:
                logger.error(f"处理传感器数据时出错: {e}", exc_info=True)
                await asyncio.sleep(0.1)
                
    except asyncio.CancelledError:
        logger.info("传感器数据流任务被取消")
        raise
    except Exception as e:
        logger.error(f"传感器数据流错误: {e}", exc_info=True)
    finally:
        _sensor_running = False
        logger.info("传感器数据流已停止")


async def _ensure_sensor_stream_running():
    """确保传感器数据流正在运行"""
    global _sensor_task, _sensor_running
    
    if _sensor_task is None or _sensor_task.done():
        logger.info("启动新的传感器数据流任务")
        _sensor_task = asyncio.create_task(_start_sensor_stream())
    elif _sensor_running:
        logger.info("传感器数据流已在运行")
    else:
        logger.warning("传感器任务存在但未运行，重新启动")
        _sensor_task = asyncio.create_task(_start_sensor_stream())


async def _stop_sensor_stream():
    """停止传感器数据流"""
    global _sensor_task, _sensor_running, _sensor_device
    
    logger.info("正在停止传感器数据流...")
    
    # 设置停止标志
    _sensor_running = False
    
    # 取消任务
    if _sensor_task and not _sensor_task.done():
        _sensor_task.cancel()
        try:
            await _sensor_task
        except asyncio.CancelledError:
            logger.info("传感器任务已取消")
    
    # 断开传感器连接
    async with _sensor_lock:
        if _sensor_device:
            try:
                await _sensor_device.disconnect()
                logger.info("传感器设备已断开连接")
            except Exception as e:
                logger.error(f"断开传感器连接时出错: {e}")
            finally:
                _sensor_device = None
    
    _sensor_task = None
    logger.info("传感器数据流已完全停止")


@router.websocket("/stream")
async def broker_stream(websocket: WebSocket):
    """
    WebSocket端点 - 实时推送摄像头列表更新（使用 DataManager）
    
    实现要求：
    - Requirements 10.1: 提供WebSocket端点用于流式传输摄像头列表更新
    - Requirements 10.2: 当处理方向或角度消息时，通过WebSocket广播结果摄像头列表
    - Requirements 10.4: 客户端连接时发送当前状态
    - Requirements 10.5: 优雅处理客户端断开连接
    
    使用 DataManager 统一处理消息：
    1. DataManager 订阅所有消息类型（direction_result, angle_value, ai_alert）
    2. DataManager 实现优先级和去重逻辑
    3. WebSocket 连接注册回调到 DataManager
    4. 接收经过处理的消息并发送到客户端
    
    消息格式：
    {
        "type": "current_state" | "direction_result" | "angle_value" | "ai_alert",
        "message_id": "消息ID（仅消息更新）",
        "timestamp": "ISO格式时间戳",
        "data": { ... },  # 原始消息数据（仅消息更新）
        "cameras": [...]  # 摄像头ID列表
    }
    """
    global _active_connections, _data_manager
    
    logger.info(f"Broker WebSocket connection request - Client: {websocket.client}")
    
    # 标记是否已注册回调
    callback_registered = False
    
    try:
        # 确保 broker 已初始化
        await _initialize_broker()
        
        # 确保传感器数据流正在运行
        await _ensure_sensor_stream_running()
        
        # 接受WebSocket连接
        await websocket.accept()
        
        # 更新连接计数
        async with _connections_lock:
            _active_connections += 1
            current_count = _active_connections
        
        logger.info(f"WebSocket client connected: {websocket.client} (total: {current_count})")
        
        # 创建此连接专用的回调函数
        async def on_managed_message(managed_msg: ManagedMessage):
            """处理 DataManager 发送的消息"""
            try:
                # 获取摄像头详细信息
                cameras_info = await _get_cameras_details(managed_msg.cameras)
                
                # 构建响应消息
                response = {
                    "type": managed_msg.message_type,
                    "message_id": managed_msg.message_id,
                    "timestamp": datetime.fromtimestamp(managed_msg.timestamp).isoformat(),
                    "data": _make_serializable(managed_msg.data),
                    "cameras": cameras_info,
                    "priority": managed_msg.priority,
                    "remaining_time": max(0, managed_msg.expire_time - time.time())
                }
                
                # 发送到客户端
                await websocket.send_json(response)
                logger.info(
                    f"Sent {managed_msg.message_type} to client: "
                    f"{len(managed_msg.cameras)} cameras, priority={managed_msg.priority}"
                )
                
            except Exception as e:
                logger.error(f"Error in managed message callback: {e}", exc_info=True)
        
        # 注册回调到 DataManager
        if _data_manager:
            _data_manager.register_message_callback(on_managed_message)
            callback_registered = True
            logger.info("Registered callback to DataManager")
        else:
            logger.error("DataManager not initialized")
            await websocket.close(code=1011, reason="DataManager not available")
            return
        
        # 发送当前状态
        await _send_current_state(websocket)
        
        # 保持连接活跃，等待客户端断开或发送消息
        try:
            while True:
                # 接收客户端消息（主要用于保持连接）
                try:
                    message = await websocket.receive_text()
                    logger.debug(f"Received message from client: {message}")
                    
                    # 处理客户端命令
                    if message.strip() == "refresh":
                        await _send_current_state(websocket)
                    elif message.strip() == "stats":
                        # 发送 DataManager 统计信息
                        if _data_manager:
                            stats = _data_manager.get_stats()
                            await websocket.send_json({
                                "type": "stats",
                                "timestamp": datetime.now().isoformat(),
                                "data": stats
                            })
                    
                except asyncio.TimeoutError:
                    # 超时是正常的，继续等待
                    continue
                    
        except WebSocketDisconnect:
            logger.info("Broker WebSocket client disconnected normally")
        
    except WebSocketDisconnect:
        logger.info("Broker WebSocket client disconnected during setup")
    
    except Exception as e:
        logger.error(f"Broker WebSocket error: {e}", exc_info=True)
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except:
            pass
    
    finally:
        # 注销回调
        if callback_registered and _data_manager:
            try:
                _data_manager.unregister_message_callback(on_managed_message)
                logger.info("Unregistered callback from DataManager")
            except Exception as e:
                logger.error(f"Error unregistering callback: {e}")
        
        # 更新连接计数
        async with _connections_lock:
            _active_connections = max(0, _active_connections - 1)
            remaining_count = _active_connections
        
        logger.info(f"WebSocket connection cleanup complete for {websocket.client} (remaining: {remaining_count})")
        
        # 如果没有活跃连接了，停止传感器数据流
        if remaining_count == 0:
            await _stop_sensor_stream()
            logger.info("所有客户端已断开，传感器数据流已停止")


async def _send_current_state(websocket: WebSocket):
    """发送当前状态到WebSocket客户端"""
    try:
        broker = MessageBroker.get_instance()
        camera_mapper = broker._camera_mapper
        
        if not camera_mapper:
            logger.warning("Camera mapper not available, sending empty state")
            current_state = {
                "type": "current_state",
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "directions": {},
                    "angle_ranges": []
                },
                "cameras": []
            }
        else:
            # 获取所有方向的摄像头映射
            direction_mappings = camera_mapper.get_all_direction_mappings()
            
            # 获取所有角度范围
            angle_ranges = camera_mapper.get_all_angle_ranges()
            
            # 收集所有唯一的摄像头
            all_cameras = set()
            for cameras in direction_mappings.values():
                for camera in cameras:
                    all_cameras.add(camera["id"])
            
            for angle_range in angle_ranges:
                for camera in angle_range.get("cameras", []):
                    all_cameras.add(camera["id"])
            
            current_state = {
                "type": "current_state",
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "directions": direction_mappings,
                    "angle_ranges": angle_ranges
                },
                "cameras": list(all_cameras)
            }
        
        await websocket.send_json(current_state)
        logger.info("Sent current state to WebSocket client")
        
    except Exception as e:
        logger.error(f"Error sending current state: {e}", exc_info=True)
        # 发送错误消息
        try:
            error_message = {
                "type": "error",
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "error": f"Failed to get current state: {str(e)}"
                },
                "cameras": []
            }
            await websocket.send_json(error_message)
        except:
            pass


@router.get("/mappings")
async def get_current_mappings():
    """
    HTTP端点 - 查询当前摄像头映射
    
    实现要求：
    - Requirements 10.3: 提供HTTP端点查询当前摄像头映射
    
    Returns:
        Dict: 包含所有方向和角度范围的摄像头映射
    """
    global _active_connections
    
    try:
        
        broker = MessageBroker.get_instance()
        camera_mapper = broker._camera_mapper
        
        if not camera_mapper:
            raise HTTPException(
                status_code=503, 
                detail="Camera mapper not available"
            )
        
        # 获取所有方向的摄像头映射
        direction_mappings = camera_mapper.get_all_direction_mappings()
        
        # 获取所有角度范围
        angle_ranges = camera_mapper.get_all_angle_ranges()
        
        # 获取统计信息
        broker_stats = broker.get_stats()
        
        return {
            "directions": direction_mappings,
            "angle_ranges": angle_ranges,
            "timestamp": datetime.now().isoformat(),
            "stats": {
                "registered_message_types": broker.get_registered_types(),
                "total_subscribers": broker.get_subscriber_count(),
                "messages_published": broker_stats.get("messages_published", 0),
                "messages_failed": broker_stats.get("messages_failed", 0),
                "active_websocket_connections": _active_connections
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current mappings: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get current mappings: {str(e)}"
        )


@router.get("/status")
async def get_broker_status():
    """
    获取消息代理状态
    
    Returns:
        Dict: 消息代理的状态信息
    """
    global _active_connections, _data_manager
    
    try:
        await _initialize_broker()
        
        broker = MessageBroker.get_instance()
        stats = broker.get_stats()
        
        # 获取 DataManager 状态
        data_manager_stats = None
        if _data_manager:
            data_manager_stats = _data_manager.get_stats()
        
        return {
            "status": "running",
            "initialized": _broker_initialized,
            "registered_types": broker.get_registered_types(),
            "subscriber_counts": {
                msg_type: broker.get_subscriber_count(msg_type)
                for msg_type in broker.get_registered_types()
            },
            "total_subscribers": broker.get_subscriber_count(),
            "websocket_connections": _active_connections,
            "stats": stats,
            "data_manager": data_manager_stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting broker status: {e}", exc_info=True)
        return {
            "status": "error",
            "initialized": _broker_initialized,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@router.post("/test/publish")
async def test_publish_message(
    message_type: str,
    data: Dict[str, Any]
):
    """
    测试端点 - 手动发布消息到消息代理
    
    用于测试 MessageBroker 的消息发布和处理功能。
    
    Args:
        message_type: 消息类型 (direction_result, angle_value, ai_alert)
        data: 消息数据
        
    Returns:
        Dict: 发布结果，包含成功状态、消息ID、通知的订阅者数量等
        
    Example:
        POST /api/broker/test/publish?message_type=direction_result
        Body: {"command": "forward", "confidence": 0.95}
    """
    try:

        
        broker = MessageBroker.get_instance()
        
        # 检查消息类型是否已注册
        if not broker.is_type_registered(message_type):
            raise HTTPException(
                status_code=400,
                detail=f"Message type '{message_type}' is not registered. "
                       f"Available types: {broker.get_registered_types()}"
            )
        
        # 发布消息
        result = broker.publish(message_type, data)
        
        # 获取对应的摄像头列表
        message = MessageData(
            type=message_type,
            data=data,
            timestamp=datetime.now()
        )
        cameras = await _get_cameras_for_message(message)
        
        return {
            "success": result.success,
            "message_id": result.message_id,
            "message_type": message_type,
            "subscribers_notified": result.subscribers_notified,
            "cameras_matched": len(cameras),
            "cameras": [cam.to_dict() for cam in cameras],
            "errors": result.errors,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error publishing test message: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to publish message: {str(e)}"
        )


@router.get("/test/info")
async def test_broker_info():
    """
    测试端点 - 获取消息代理详细信息
    
    返回消息代理的完整状态，包括：
    - 已注册的消息类型及其处理器
    - 每种消息类型的订阅者信息
    - 统计数据
    - WebSocket 连接状态
    
    Returns:
        Dict: 消息代理的详细信息
    """
    global _active_connections
    
    try:
        
        broker = MessageBroker.get_instance()
        stats = broker.get_stats()
        registered_types = broker.get_registered_types()
        
        # 获取每种消息类型的详细信息
        type_details = {}
        for msg_type in registered_types:
            handler = broker.get_handler(msg_type)
            subscribers = broker.get_subscribers(msg_type)
            
            type_details[msg_type] = {
                "handler": handler.__class__.__name__ if handler else None,
                "subscriber_count": len(subscribers),
                "subscribers": subscribers
            }
        
        # 获取摄像头映射器信息
        camera_mapper = broker._camera_mapper
        mapper_info = None
        if camera_mapper:
            direction_mappings = camera_mapper.get_all_direction_mappings()
            angle_ranges = camera_mapper.get_all_angle_ranges()
            
            mapper_info = {
                "available": True,
                "direction_count": len(direction_mappings),
                "directions": list(direction_mappings.keys()),
                "angle_range_count": len(angle_ranges)
            }
        else:
            mapper_info = {"available": False}
        
        return {
            "broker": {
                "initialized": _broker_initialized,
                "registered_types": registered_types,
                "type_details": type_details,
                "total_subscribers": broker.get_subscriber_count(),
                "stats": stats
            },
            "camera_mapper": mapper_info,
            "websocket": {
                "active_connections": _active_connections
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting broker info: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get broker info: {str(e)}"
        )