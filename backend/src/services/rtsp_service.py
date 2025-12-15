"""
RTSP 流服务
负责从 RTSP 源读取视频流并编码为 JPEG 帧
使用 RTSCapture 解决实时流缓冲区延迟问题
"""
import asyncio
import cv2
import logging
from typing import Optional, Dict
from datetime import datetime

from ..utils.rts_capture import RTSCapture

logger = logging.getLogger(__name__)


class RTSPStreamService:
    """RTSP 流服务类"""
    
    def __init__(self):
        self.active_streams: Dict[str, RTSCapture] = {}
        self.stream_tasks: Dict[str, asyncio.Task] = {}
        
    def start_stream(self, stream_id: str, rtsp_url: str) -> bool:
        """
        启动 RTSP 流
        
        Args:
            stream_id: 流标识符
            rtsp_url: RTSP URL
            
        Returns:
            是否成功启动
        """
        if stream_id in self.active_streams:
            logger.info(f"Stream {stream_id} already exists, reusing existing capture")
            return True
            
        try:
            # 使用 RTSCapture 创建实时流捕获
            cap = RTSCapture.create(rtsp_url)
            if not cap.isOpened():
                logger.error(f"Failed to open RTSP stream: {rtsp_url}")
                return False
            
            # 启动实时帧读取线程
            cap.start_read()
            
            # 验证流是否正常工作
            if not cap.isStarted():
                logger.error(f"Failed to start real-time capture for stream: {rtsp_url}")
                cap.release()
                return False
                
            self.active_streams[stream_id] = cap
            logger.info(f"Started RTSP stream {stream_id}: {rtsp_url} (RTSCapture mode)")
            return True
            
        except Exception as e:
            logger.error(f"Error starting stream {stream_id}: {e}")
            return False
    
    def stop_stream(self, stream_id: str) -> bool:
        """
        停止 RTSP 流
        
        Args:
            stream_id: 流标识符
            
        Returns:
            是否成功停止
        """
        if stream_id not in self.active_streams:
            logger.warning(f"Stream {stream_id} not found")
            return False
            
        try:
            cap = self.active_streams[stream_id]
            # RTSCapture 的 release 方法会自动停止读取线程
            cap.release()
            del self.active_streams[stream_id]
            
            # 取消相关任务
            if stream_id in self.stream_tasks:
                self.stream_tasks[stream_id].cancel()
                del self.stream_tasks[stream_id]
                
            logger.info(f"Stopped RTSP stream {stream_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping stream {stream_id}: {e}")
            return False
    
    def get_frame(self, stream_id: str) -> Optional[bytes]:
        """
        获取单帧图像（JPEG 编码）- 使用 RTSCapture 获取最新帧
        
        Args:
            stream_id: 流标识符
            
        Returns:
            JPEG 编码的图像字节，失败返回 None
        """
        if stream_id not in self.active_streams:
            logger.warning(f"Stream {stream_id} not found")
            return None
            
        try:
            cap = self.active_streams[stream_id]
            
            # 使用 RTSCapture 的内置方法获取最新帧并编码
            frame_bytes = cap.get_latest_frame_bytes(quality=85)
            
            if frame_bytes is None:
                logger.warning(f"Failed to get latest frame from stream {stream_id}")
                return None
                
            return frame_bytes
            
        except Exception as e:
            logger.error(f"Error getting frame from stream {stream_id}: {e}")
            return None
    
    def get_latest_frame(self, stream_id: str) -> Optional[bytes]:
        """
        获取最新帧（高性能模式）
        
        Args:
            stream_id: 流标识符
            
        Returns:
            JPEG 编码的图像字节，失败返回 None
        """
        if stream_id not in self.active_streams:
            logger.warning(f"Stream {stream_id} not found")
            return None
            
        try:
            cap = self.active_streams[stream_id]
            
            # 使用更低质量和更快编码以提高帧率
            frame_bytes = cap.get_latest_frame_bytes(quality=60)
            
            if frame_bytes is None:
                logger.warning(f"Failed to get latest frame from stream {stream_id}")
                return None
                
            return frame_bytes
            
        except Exception as e:
            logger.error(f"Error getting latest frame from stream {stream_id}: {e}")
            return None
    
    def get_high_fps_frame(self, stream_id: str) -> Optional[bytes]:
        """
        获取最新帧（超高帧率模式）
        
        Args:
            stream_id: 流标识符
            
        Returns:
            JPEG 编码的图像字节，失败返回 None
        """
        if stream_id not in self.active_streams:
            return None
            
        try:
            cap = self.active_streams[stream_id]
            
            # 使用快速编码方法以获得最高帧率
            frame_bytes = cap.get_fast_frame_bytes(quality=40)
            
            return frame_bytes
            
        except Exception as e:
            logger.error(f"Error getting high fps frame from stream {stream_id}: {e}")
            return None

    def get_stream_info(self, stream_id: str) -> Optional[Dict]:
        """
        获取流信息
        
        Args:
            stream_id: 流标识符
            
        Returns:
            流信息字典
        """
        if stream_id not in self.active_streams:
            return None
            
        try:
            cap = self.active_streams[stream_id]
            return {
                "stream_id": stream_id,
                "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                "fps": int(cap.get(cv2.CAP_PROP_FPS)),
                "buffer_size": int(cap.get(cv2.CAP_PROP_BUFFERSIZE)),
                "is_opened": cap.isOpened(),
                "is_started": cap.isStarted(),
                "rts_capture_mode": True,
                "real_time_streaming": cap._reading
            }
        except Exception as e:
            logger.error(f"Error getting stream info for {stream_id}: {e}")
            return None
    
    def list_streams(self) -> list:
        """
        列出所有活动流
        
        Returns:
            流 ID 列表
        """
        return list(self.active_streams.keys())
    
    def cleanup(self):
        """清理所有流"""
        for stream_id in list(self.active_streams.keys()):
            self.stop_stream(stream_id)


# 全局实例
rtsp_service = RTSPStreamService()
