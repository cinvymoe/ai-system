"""
RTSP WebSocket API
提供 RTSP 流的 WebSocket 接口
"""
import asyncio
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from typing import Dict, Set
from pydantic import BaseModel

from ..services.rtsp_service import rtsp_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rtsp", tags=["rtsp"])


class RTSPStreamRequest(BaseModel):
    """RTSP 流请求模型"""
    stream_id: str
    rtsp_url: str


class RTSPStreamResponse(BaseModel):
    """RTSP 流响应模型"""
    success: bool
    message: str
    stream_id: str


# 存储每个流的 WebSocket 连接
active_connections: Dict[str, Set[WebSocket]] = {}


@router.post("/streams/start", response_model=RTSPStreamResponse)
async def start_stream(request: RTSPStreamRequest):
    """
    启动 RTSP 流
    
    Args:
        request: 包含 stream_id 和 rtsp_url 的请求
        
    Returns:
        操作结果
    """
    success = rtsp_service.start_stream(request.stream_id, request.rtsp_url)
    
    if success:
        # 初始化连接集合
        if request.stream_id not in active_connections:
            active_connections[request.stream_id] = set()
            
        return RTSPStreamResponse(
            success=True,
            message=f"Stream {request.stream_id} started successfully",
            stream_id=request.stream_id
        )
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to start stream {request.stream_id}"
        )


@router.post("/streams/stop/{stream_id}", response_model=RTSPStreamResponse)
async def stop_stream(stream_id: str):
    """
    停止 RTSP 流的 WebSocket 连接（不清理 capture）
    
    Args:
        stream_id: 流标识符
        
    Returns:
        操作结果
    """
    # 只关闭所有相关的 WebSocket 连接，不清理 capture
    if stream_id in active_connections:
        for ws in list(active_connections[stream_id]):
            try:
                await ws.close()
            except Exception as e:
                logger.warning(f"Error closing WebSocket for stream {stream_id}: {e}")
        try:
            del active_connections[stream_id]
        except KeyError:
            logger.warning(f"Stream {stream_id} already removed from active_connections")
        
        logger.info(f"Closed WebSocket connections for stream {stream_id}, capture remains active")
        return RTSPStreamResponse(
            success=True,
            message=f"WebSocket connections for stream {stream_id} closed successfully",
            stream_id=stream_id
        )
    else:
        # 没有活动连接
        logger.warning(f"No active WebSocket connections for stream {stream_id}")
        return RTSPStreamResponse(
            success=True,
            message=f"No active connections for stream {stream_id}",
            stream_id=stream_id
        )


@router.post("/streams/cleanup/{stream_id}", response_model=RTSPStreamResponse)
async def cleanup_stream(stream_id: str):
    """
    清理 RTSP 流（关闭 WebSocket 并释放 capture）
    
    Args:
        stream_id: 流标识符
        
    Returns:
        操作结果
    """
    # 先关闭所有 WebSocket 连接
    if stream_id in active_connections:
        for ws in list(active_connections[stream_id]):
            try:
                await ws.close()
            except Exception as e:
                logger.warning(f"Error closing WebSocket for stream {stream_id}: {e}")
        try:
            del active_connections[stream_id]
        except KeyError:
            logger.warning(f"Stream {stream_id} already removed from active_connections")
    
    # 清理 capture
    success = rtsp_service.stop_stream(stream_id)
    
    if success:
        return RTSPStreamResponse(
            success=True,
            message=f"Stream {stream_id} cleaned up successfully",
            stream_id=stream_id
        )
    else:
        # 即使流不存在，也返回成功（幂等性）
        logger.warning(f"Stream {stream_id} not found, but returning success for idempotency")
        return RTSPStreamResponse(
            success=True,
            message=f"Stream {stream_id} already cleaned up or not found",
            stream_id=stream_id
        )


@router.get("/streams")
async def list_streams():
    """
    列出所有活动流
    
    Returns:
        流列表及其信息
    """
    streams = rtsp_service.list_streams()
    stream_info = []
    
    for stream_id in streams:
        info = rtsp_service.get_stream_info(stream_id)
        if info:
            info["connections"] = len(active_connections.get(stream_id, set()))
            stream_info.append(info)
    
    return {
        "streams": stream_info,
        "total": len(stream_info)
    }


@router.get("/streams/{stream_id}")
async def get_stream_info(stream_id: str):
    """
    获取流信息
    
    Args:
        stream_id: 流标识符
        
    Returns:
        流信息
    """
    info = rtsp_service.get_stream_info(stream_id)
    
    if info:
        info["connections"] = len(active_connections.get(stream_id, set()))
        return info
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Stream {stream_id} not found"
        )


@router.websocket("/ws/{stream_id}")
async def websocket_stream(websocket: WebSocket, stream_id: str):
    """
    WebSocket 端点，用于传输 RTSP 视频流
    
    Args:
        websocket: WebSocket 连接
        stream_id: 流标识符
    """
    await websocket.accept()
    
    # 检查流是否存在
    if stream_id not in rtsp_service.list_streams():
        await websocket.send_json({
            "type": "error",
            "message": f"Stream {stream_id} not found"
        })
        await websocket.close()
        return
    
    # 添加到活动连接
    if stream_id not in active_connections:
        active_connections[stream_id] = set()
    active_connections[stream_id].add(websocket)
    
    logger.info(f"WebSocket connected for stream {stream_id}")
    
    try:
        # 发送连接成功消息
        await websocket.send_json({
            "type": "connected",
            "stream_id": stream_id,
            "message": "Connected to RTSP stream"
        })
        
        # 持续发送视频帧
        while True:
            frame_data = rtsp_service.get_latest_frame(stream_id)
            
            if frame_data:
                # 发送二进制帧数据
                await websocket.send_bytes(frame_data)
            else:
                # 流读取失败，发送错误消息
                await websocket.send_json({
                    "type": "error",
                    "message": "Failed to read frame"
                })
                await asyncio.sleep(0.1)  # 减少错误重试间隔
                continue
            
            # 控制帧率（约 60 FPS）- 提高帧率
            await asyncio.sleep(0.016)
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for stream {stream_id}")
    except Exception as e:
        logger.error(f"Error in WebSocket stream {stream_id}: {e}")
    finally:
        # 移除连接
        if stream_id in active_connections:
            active_connections[stream_id].discard(websocket)
            if not active_connections[stream_id]:
                del active_connections[stream_id]


@router.websocket("/ws/high-fps/{stream_id}")
async def websocket_high_fps_stream(websocket: WebSocket, stream_id: str):
    """
    高帧率 WebSocket 端点，用于传输 RTSP 视频流
    
    Args:
        websocket: WebSocket 连接
        stream_id: 流标识符
    """
    await websocket.accept()
    
    # 检查流是否存在
    if stream_id not in rtsp_service.list_streams():
        await websocket.send_json({
            "type": "error",
            "message": f"Stream {stream_id} not found"
        })
        await websocket.close()
        return
    
    # 添加到活动连接
    if stream_id not in active_connections:
        active_connections[stream_id] = set()
    active_connections[stream_id].add(websocket)
    
    logger.info(f"High-FPS WebSocket connected for stream {stream_id}")
    
    try:
        # 发送连接成功消息
        await websocket.send_json({
            "type": "connected",
            "stream_id": stream_id,
            "message": "Connected to high-FPS RTSP stream",
            "mode": "high-fps"
        })
        
        # 持续发送视频帧（高帧率模式）
        while True:
            frame_data = rtsp_service.get_high_fps_frame(stream_id)
            
            if frame_data:
                # 发送二进制帧数据
                await websocket.send_bytes(frame_data)
            else:
                # 流读取失败，跳过这一帧
                await asyncio.sleep(0.005)
                continue
            
            # 控制帧率（约 120 FPS）- 超高帧率
            await asyncio.sleep(0.008)
            
    except WebSocketDisconnect:
        logger.info(f"High-FPS WebSocket disconnected for stream {stream_id}")
    except Exception as e:
        logger.error(f"Error in high-FPS WebSocket stream {stream_id}: {e}")
    finally:
        # 移除连接
        if stream_id in active_connections:
            active_connections[stream_id].discard(websocket)
            if not active_connections[stream_id]:
                del active_connections[stream_id]
