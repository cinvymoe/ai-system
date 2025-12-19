"""API endpoints for person detection monitoring."""
import logging
import asyncio
import cv2
import base64
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Optional, Dict, Set

try:
    from scheduler.person_detector import get_person_detection_monitor, read_latest_drawn_frame
    from services.camera_service import CameraService
    from repositories.camera_repository import CameraRepository
    from utils.rts_capture import RTSCapture
    from database import SessionLocal
except ImportError:
    from src.scheduler.person_detector import get_person_detection_monitor, read_latest_drawn_frame
    from src.services.camera_service import CameraService
    from src.repositories.camera_repository import CameraRepository
    from src.utils.rts_capture import RTSCapture
    from src.database import SessionLocal

logger = logging.getLogger(__name__)

# WebSocket 连接管理
active_detection_connections: Dict[str, Set[WebSocket]] = {}

router = APIRouter(prefix="/api/person-detection", tags=["person-detection"])


class PersonDetectionConfig(BaseModel):
    """Configuration for person detection monitor."""
    model_path: Optional[str] = None
    check_interval_seconds: int = 30


class PersonDetectionStatus(BaseModel):
    """Status response for person detection monitor."""
    is_running: bool
    check_interval_seconds: int
    last_check_time: Optional[str]
    total_detections: int
    total_persons_detected: int
    detector_initialized: bool
    next_check_time: Optional[str]


@router.post("/start")
async def start_person_detection(config: PersonDetectionConfig):
    """Start the person detection monitor.
    
    Args:
        config: Configuration with model path and check interval
        
    Returns:
        Status message
    """
    try:
        # Import settings to get default model path
        try:
            from config import settings
        except ImportError:
            from src.config import settings
        
        # Use provided model path or default from config
        model_path = config.model_path or settings.PERSON_DETECTION_MODEL_PATH
        
        monitor = get_person_detection_monitor(
            model_path=model_path,
            check_interval_seconds=config.check_interval_seconds
        )
        
        if monitor.is_running:
            return {
                "status": "already_running",
                "message": "Person detection monitor is already running"
            }
        
        monitor.start()
        
        return {
            "status": "started",
            "message": f"Person detection monitor started with {config.check_interval_seconds}s interval",
            "config": {
                "model_path": model_path,
                "check_interval_seconds": config.check_interval_seconds
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to start person detection monitor: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/start-default")
async def start_person_detection_default():
    """Start the person detection monitor with default settings.
    
    Uses the default model path from config and 30-second interval.
    
    Returns:
        Status message
    """
    try:
        # Import settings to get default model path
        try:
            from config import settings
        except ImportError:
            from src.config import settings
        
        monitor = get_person_detection_monitor(
            model_path=settings.PERSON_DETECTION_MODEL_PATH,
            check_interval_seconds=30
        )
        
        if monitor.is_running:
            return {
                "status": "already_running",
                "message": "Person detection monitor is already running"
            }
        
        monitor.start()
        
        return {
            "status": "started",
            "message": "Person detection monitor started with default settings",
            "config": {
                "model_path": settings.PERSON_DETECTION_MODEL_PATH,
                "check_interval_seconds": 30
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to start person detection monitor with defaults: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop")
async def stop_person_detection():
    """Stop the person detection monitor.
    
    Returns:
        Status message
    """
    try:
        # Get existing monitor instance from factory module
        try:
            from scheduler.detection.factory import _detection_monitor_instance
        except ImportError:
            from src.scheduler.detection.factory import _detection_monitor_instance
        
        if _detection_monitor_instance is None:
            return {
                "status": "not_running",
                "message": "Person detection monitor is not running"
            }
        
        _detection_monitor_instance.stop()
        
        return {
            "status": "stopped",
            "message": "Person detection monitor stopped successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to stop person detection monitor: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=PersonDetectionStatus)
async def get_person_detection_status():
    """Get current status of the person detection monitor.
    
    Returns:
        Current monitor status
    """
    try:
        try:
            from scheduler.detection.factory import _detection_monitor_instance
        except ImportError:
            from src.scheduler.detection.factory import _detection_monitor_instance
        
        if _detection_monitor_instance is None:
            return PersonDetectionStatus(
                is_running=False,
                check_interval_seconds=0,
                last_check_time=None,
                total_detections=0,
                total_persons_detected=0,
                detector_initialized=False,
                next_check_time=None
            )
        
        status = _detection_monitor_instance.get_status()
        return PersonDetectionStatus(**status)
        
    except Exception as e:
        logger.error(f"Failed to get person detection status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/detect-now")
async def trigger_detection_now():
    """Trigger an immediate person detection run.
    
    Returns:
        Status message
    """
    try:
        try:
            from scheduler.detection.factory import _detection_monitor_instance
        except ImportError:
            from src.scheduler.detection.factory import _detection_monitor_instance
        
        if _detection_monitor_instance is None:
            raise HTTPException(
                status_code=400, 
                detail="Person detection monitor is not initialized"
            )
        
        if not _detection_monitor_instance.is_running:
            raise HTTPException(
                status_code=400,
                detail="Person detection monitor is not running"
            )
        
        # Trigger immediate detection
        _detection_monitor_instance.detect_on_cameras()
        
        return {
            "status": "success",
            "message": "Person detection triggered successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to trigger person detection: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/frame-info/{camera_id}")
async def get_frame_info(camera_id: str):
    """Get information about stored frame for a camera.
    
    Args:
        camera_id: Camera ID to get frame info for
        
    Returns:
        Frame information including timestamp and shape
    """
    try:
        from src.scheduler.person_detector import get_frame_info
        
        info = get_frame_info(camera_id)
        return {
            "status": "success",
            "frame_info": info
        }
        
    except Exception as e:
        logger.error(f"Failed to get frame info for camera {camera_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear-frames")
async def clear_frame_storage(camera_id: Optional[str] = None):
    """Clear frame storage for a specific camera or all cameras.
    
    Args:
        camera_id: Camera ID to clear, or None to clear all
        
    Returns:
        Status message
    """
    try:
        from src.scheduler.person_detector import clear_frame_storage
        
        clear_frame_storage(camera_id)
        
        if camera_id:
            message = f"Frame storage cleared for camera {camera_id}"
        else:
            message = "All frame storage cleared"
            
        return {
            "status": "success",
            "message": message
        }
        
    except Exception as e:
        logger.error(f"Failed to clear frame storage: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/ws/{stream_id}")
async def websocket_person_detection_stream(websocket: WebSocket, stream_id: str):
    """
    WebSocket 端点，用于传输带有人员检测标注的视频流
    
    Args:
        websocket: WebSocket 连接
        stream_id: 流标识符（camera_id）
    """
    await websocket.accept()
    
    # 添加到活动连接
    if stream_id not in active_detection_connections:
        active_detection_connections[stream_id] = set()
    active_detection_connections[stream_id].add(websocket)
    
    logger.info(f"Person detection WebSocket connected for stream {stream_id}")
    
    try:
        # 持续处理和发送帧
        while True:
            try:
                # 直接从全局帧存储中获取已处理的帧（带检测标注）
                ret, annotated_frame, frame_timestamp, detections = read_latest_drawn_frame(stream_id)
                
                if not ret or annotated_frame is None:
                    await websocket.send_json({
                        "type": "error",
                        "message": "No processed frame available from person detection monitor"
                    })
                    await asyncio.sleep(0.5)  # 等待更长时间让检测器捕获帧
                    continue
                
                # 编码图像为 JPEG
                _, buffer = cv2.imencode('.jpg', annotated_frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                
                if buffer is not None:
                    # 发送处理后的图像数据
                    frame_data = buffer.tobytes()
                    await websocket.send_bytes(frame_data)
                    
                    # 发送检测信息（无论是否有人）
                    detection_info = {
                        "type": "detection",
                        "timestamp": frame_timestamp.isoformat() if frame_timestamp else None,
                        "current_time": asyncio.get_event_loop().time(),
                        "person_count": len([d for d in detections if d['class'] == 'person']) if detections else 0,
                        "detections": detections or []
                    }
                    await websocket.send_json(detection_info)
                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Failed to encode frame"
                    })
                
                # 控制帧率（约 15 FPS 以减少计算负载）
                await asyncio.sleep(0.067)
                
            except Exception as e:
                logger.error(f"Error processing frame for stream {stream_id}: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": f"Frame processing error: {str(e)}"
                })
                await asyncio.sleep(0.1)
                continue
        
    except WebSocketDisconnect:
        logger.info(f"Person detection WebSocket disconnected for stream {stream_id}")
    except Exception as e:
        logger.error(f"Error in person detection WebSocket stream {stream_id}: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"WebSocket error: {str(e)}"
            })
        except:
            pass
    finally:
        logger.info(f"Person disconnect WebSocket connected for stream {stream_id}")

        # 移除连接
        if stream_id in active_detection_connections:
            active_detection_connections[stream_id].discard(websocket)
            if not active_detection_connections[stream_id]:
                del active_detection_connections[stream_id]
