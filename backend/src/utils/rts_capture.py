#!/usr/bin/env python3
# encoding: utf-8
"""
Real Time Streaming Capture
基于提供的 RTSCapture 实现，解决 OpenCV VideoCapture 缓冲区延迟问题

经过测试 cv2.VideoCapture 的 read 函数并不能获取实时流的最新帧
而是按照内部缓冲区中顺序逐帧的读取，opencv会每过一段时间清空一次缓冲区
但是清空的时机并不是我们能够控制的，因此如果对视频帧的处理速度如果跟不上接受速度
那么每过一段时间，在播放时会看到画面突然花屏，甚至程序直接崩溃

处理方式：使用一个临时缓存保存最新一帧，开启一个线程读取最新帧保存到缓存里
用户读取的时候只返回最新的一帧
"""
import threading
import cv2
import logging
from typing import Optional, Tuple
import numpy as np

logger = logging.getLogger(__name__)


class RTSCapture(cv2.VideoCapture):
    """
    Real Time Streaming Capture.
    这个类必须使用 RTSCapture.create 方法创建，请不要直接实例化
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cur_frame: Optional[np.ndarray] = None
        self._reading = False
        self._frame_lock = threading.Lock()
        self.frame_receiver: Optional[threading.Thread] = None
        self.schemes = ["rtsp://", "rtmp://", "http://", "https://"]  # 用于识别实时流
        
    @staticmethod
    def create(url, *schemes):
        """
        实例化&初始化
        
        Args:
            url: 视频流 URL 或设备索引
            *schemes: 额外的流协议方案
            
        Returns:
            RTSCapture 实例
            
        Example:
            rtscap = RTSCapture.create("rtsp://example.com/live/1")
            or
            rtscap = RTSCapture.create("http://example.com/live/1.m3u8", "http://")
        """
        rtscap = RTSCapture(url)
        rtscap.schemes.extend(schemes)
        
        # 判断是否为实时流
        if isinstance(url, str) and url.startswith(tuple(rtscap.schemes)):
            rtscap._reading = True
            logger.info(f"Created RTSCapture for streaming URL: {url}")
        elif isinstance(url, int):
            # 这里可能是本机设备
            logger.info(f"Created RTSCapture for local device: {url}")
        else:
            logger.info(f"Created RTSCapture for file: {url}")
            
        # 配置 VideoCapture 参数以减少延迟
        try:
            rtscap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # 最小缓冲区
            rtscap.set(cv2.CAP_PROP_FPS, 60)  # 设置更高帧率
            
            # RTSP 特定优化
            if isinstance(url, str) and url.startswith("rtsp://"):
                rtscap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 3000)  # 3秒连接超时
                rtscap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, 1000)  # 1秒读取超时
                
            # 默认使用H264格式
            try:
                rtscap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('H', '2', '6', '4'))
            except:
                pass
                
        except Exception as e:
            logger.warning(f"Failed to set capture properties: {e}")
            
        return rtscap
    
    def isStarted(self):
        """
        替代 VideoCapture.isOpened()
        检查捕获是否已启动并且线程是否活跃
        """
        ok = self.isOpened()
        if ok and self._reading and self.frame_receiver:
            ok = self.frame_receiver.is_alive()
        return ok
    
    def recv_frame(self):
        """
        子线程读取最新视频帧方法
        持续读取帧并保存最新的一帧
        """
        logger.info("Frame receiver thread started")
        
        while self._reading and self.isOpened():
            try:
                ok, frame = super().read()  # 调用父类的 read 方法
                if not ok:
                    logger.warning("Failed to read frame, stopping receiver")
                    break
                    
                # 线程安全地更新当前帧
                with self._frame_lock:
                    self._cur_frame = frame.copy() if frame is not None else None
                    
            except Exception as e:
                logger.error(f"Error in frame receiver: {e}")
                break
                
        self._reading = False
        logger.info("Frame receiver thread stopped")
    
    def read2(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        读取最新视频帧
        
        Returns:
            (success, frame): 返回结果格式与 VideoCapture.read() 一样
        """
        with self._frame_lock:
            frame = self._cur_frame
            # 不清空当前帧，允许重复读取同一帧
            
        return frame is not None, frame
    
    def read_latest_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        读取最新帧的别名方法
        在 start_read() 后会被动态指向正确的读取方法
        """
        return self.read()
    
    def start_read(self):
        """
        启动子线程读取视频帧
        """
        if self._reading and not (self.frame_receiver and self.frame_receiver.is_alive()):
            self.frame_receiver = threading.Thread(target=self.recv_frame, daemon=True)
            self.frame_receiver.start()
            
            # 动态改变读取方法的指向
            self.read_latest_frame = self.read2
            logger.info("Started real-time frame reading thread")
        else:
            # 对于非实时流，使用普通的 read 方法
            self.read_latest_frame = self.read
            logger.info("Using standard read method for non-streaming source")
    
    def stop_read(self):
        """
        退出子线程方法
        """
        self._reading = False
        if self.frame_receiver and self.frame_receiver.is_alive():
            self.frame_receiver.join(timeout=2.0)  # 等待最多2秒
            if self.frame_receiver.is_alive():
                logger.warning("Frame receiver thread did not stop gracefully")
        
        # 重置读取方法
        self.read_latest_frame = self.read
        logger.info("Stopped frame reading thread")
    
    def get_latest_frame_bytes(self, quality: int = 85) -> Optional[bytes]:
        """
        获取最新帧并编码为 JPEG 字节
        
        Args:
            quality: JPEG 质量 (0-100)
            
        Returns:
            JPEG 编码的字节数据，失败返回 None
        """
        ok, frame = self.read_latest_frame()
        if not ok or frame is None:
            return None
            
        try:
            # 处理颜色空间转换以避免yuvj420p警告
            if len(frame.shape) == 3 and frame.shape[2] == 3:
                # 确保是BGR格式
                if frame.dtype != np.uint8:
                    frame = frame.astype(np.uint8)
            elif len(frame.shape) == 2:
                # 灰度图转BGR
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
            
            # 优化编码参数以提高速度
            encode_params = [
                cv2.IMWRITE_JPEG_QUALITY, quality,
                cv2.IMWRITE_JPEG_OPTIMIZE, 0,  # 关闭优化以提高速度
                cv2.IMWRITE_JPEG_PROGRESSIVE, 0,  # 关闭渐进式编码
                cv2.IMWRITE_JPEG_RST_INTERVAL, 0  # 关闭重启间隔
            ]
            
            ret, buffer = cv2.imencode('.jpg', frame, encode_params)
            if ret:
                return buffer.tobytes()
        except Exception as e:
            logger.error(f"Failed to encode frame: {e}")
            
        return None
    
    def get_fast_frame_bytes(self, quality: int = 50) -> Optional[bytes]:
        """
        获取最新帧并快速编码为 JPEG 字节（超高速模式）
        
        Args:
            quality: JPEG 质量 (0-100)，默认50以获得最佳速度
            
        Returns:
            JPEG 编码的字节数据，失败返回 None
        """
        ok, frame = self.read_latest_frame()
        if not ok or frame is None:
            return None
            
        try:
            # 处理颜色空间转换以避免yuvj420p警告
            if len(frame.shape) == 3 and frame.shape[2] == 3:
                # 确保是BGR格式
                if frame.dtype != np.uint8:
                    frame = frame.astype(np.uint8)
            elif len(frame.shape) == 2:
                # 灰度图转BGR
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
            
            # 最快编码参数
            encode_params = [
                cv2.IMWRITE_JPEG_QUALITY, quality,
                cv2.IMWRITE_JPEG_OPTIMIZE, 0,
                cv2.IMWRITE_JPEG_PROGRESSIVE, 0,
                cv2.IMWRITE_JPEG_RST_INTERVAL, 0
            ]
            
            ret, buffer = cv2.imencode('.jpg', frame, encode_params)
            if ret:
                return buffer.tobytes()
        except Exception as e:
            logger.error(f"Failed to fast encode frame: {e}")
            
        return None
    
    def release(self):
        """
        释放资源
        """
        self.stop_read()
        super().release()
        logger.info("RTSCapture released")


def test_rtscapture(url: str):
    """
    测试 RTSCapture 功能
    
    Args:
        url: 测试的视频流 URL
    """
    import sys
    
    rtscap = RTSCapture.create(url)
    if not rtscap.isOpened():
        print(f"Failed to open: {url}")
        return
        
    rtscap.start_read()  # 启动子线程并改变 read_latest_frame 的指向
    
    print(f"Testing RTSCapture with: {url}")
    print("Press 'q' to quit")
    
    frame_count = 0
    try:
        while rtscap.isStarted():
            ok, frame = rtscap.read_latest_frame()  # read_latest_frame() 替代 read()
            
            if not ok or frame is None:
                print("No frame available")
                continue
                
            frame_count += 1
            
            # 显示帧信息
            if frame_count % 30 == 0:  # 每30帧显示一次信息
                h, w = frame.shape[:2]
                print(f"Frame {frame_count}: {w}x{h}")
            
            # 如果有显示环境，显示图像
            try:
                cv2.imshow("RTSCapture Test", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            except:
                # 无显示环境时跳过显示
                pass
                
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    finally:
        rtscap.stop_read()
        rtscap.release()
        cv2.destroyAllWindows()
        print(f"Test completed. Total frames: {frame_count}")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print('python3 rts_capture.py "rtsp://xxx"')
        print('python3 rts_capture.py "http://xxx.m3u8"')
        sys.exit(1)
        
    test_rtscapture(sys.argv[1])