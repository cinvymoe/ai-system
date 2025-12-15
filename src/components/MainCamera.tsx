import { useEffect, useRef, useState } from 'react';
import { Video, Crosshair, Shield, AlertTriangle } from 'lucide-react';
import { Direction } from '../App';

interface MainCameraProps {
  direction: Direction;
  activeCameraId: string;
}

const directionLabels: Record<Direction, string> = {
  forward: '前进',
  backward: '后退',
  left: '左转',
  right: '右转',
  idle: '静止'
};

const directionColors: Record<Direction, string> = {
  forward: 'bg-cyan-500 shadow-cyan-500/50',
  backward: 'bg-cyan-500 shadow-cyan-500/50',
  left: 'bg-cyan-500 shadow-cyan-500/50',
  right: 'bg-cyan-500 shadow-cyan-500/50',
  idle: 'bg-slate-500 shadow-slate-500/50'
};

const RTSP_CONFIG = {
  streamId: 'main-camera',
  rtspUrl: 'rtsp://admin:cx888888@192.168.1.254/Streaming/Channels/101',
  apiBase: 'http://127.0.0.1:8000/rtsp',
  wsBase: 'ws://127.0.0.1:8000/rtsp'
};

export function MainCamera({ direction, activeCameraId }: MainCameraProps) {
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamError, setStreamError] = useState<string | null>(null);
  const [frameCount, setFrameCount] = useState(0);
  const [fps, setFps] = useState(0);
  const imgRef = useRef<HTMLImageElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const fpsCounterRef = useRef({ count: 0, lastTime: Date.now() });

  const cameraNames: Record<string, string> = {
    'camera-1': '前方摄像头',
    'camera-2': '后方摄像头',
    'camera-3': '左侧摄像头',
    'camera-4': '右侧摄像头'
  };

  // 启动 RTSP 流
  const startStream = async () => {
    try {
      const response = await fetch(`${RTSP_CONFIG.apiBase}/streams/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          stream_id: RTSP_CONFIG.streamId,
          rtsp_url: RTSP_CONFIG.rtspUrl
        })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || '启动流失败');
      }

      console.log('RTSP 流启动成功');
      connectWebSocket();
    } catch (error) {
      console.error('启动 RTSP 流失败:', error);
      setStreamError(error instanceof Error ? error.message : '启动流失败');
    }
  };

  // 连接 WebSocket
  const connectWebSocket = () => {
    const ws = new WebSocket(`${RTSP_CONFIG.wsBase}/ws/${RTSP_CONFIG.streamId}`);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('WebSocket 已连接');
      setIsStreaming(true);
      setStreamError(null);
    };

    ws.onmessage = (event) => {
      if (event.data instanceof Blob) {
        // 接收到图像帧
        const url = URL.createObjectURL(event.data);
        
        if (imgRef.current) {
          // 释放旧的 URL
          if (imgRef.current.src.startsWith('blob:')) {
            URL.revokeObjectURL(imgRef.current.src);
          }
          imgRef.current.src = url;
        }

        // 更新帧数和 FPS
        setFrameCount((prev: number) => prev + 1);
        fpsCounterRef.current.count++;
        
        const now = Date.now();
        if (now - fpsCounterRef.current.lastTime >= 1000) {
          setFps(fpsCounterRef.current.count);
          fpsCounterRef.current.count = 0;
          fpsCounterRef.current.lastTime = now;
        }
      } else {
        // JSON 消息
        try {
          const msg = JSON.parse(event.data);
          if (msg.type === 'error') {
            console.error('流错误:', msg.message);
            setStreamError(msg.message);
          } else if (msg.type === 'connected') {
            console.log('流连接成功:', msg.message);
          }
        } catch (e) {
          console.error('解析消息失败:', e);
        }
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket 错误:', error);
      setStreamError('WebSocket 连接错误');
      setIsStreaming(false);
    };

    ws.onclose = () => {
      console.log('WebSocket 已断开');
      setIsStreaming(false);
    };
  };

  // 停止 RTSP 流
  const stopStream = async () => {
    // 关闭 WebSocket
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    // 停止后端流
    try {
      await fetch(`${RTSP_CONFIG.apiBase}/streams/stop/${RTSP_CONFIG.streamId}`, {
        method: 'POST'
      });
      console.log('RTSP 流已停止');
    } catch (error) {
      console.error('停止 RTSP 流失败:', error);
    }

    setIsStreaming(false);
    setFrameCount(0);
    setFps(0);
  };

  // 组件挂载时启动流，卸载时停止流
  useEffect(() => {
    startStream();

    return () => {
      stopStream();
    };
  }, []);

  // 清理图片 URL
  useEffect(() => {
    return () => {
      if (imgRef.current && imgRef.current.src.startsWith('blob:')) {
        URL.revokeObjectURL(imgRef.current.src);
      }
    };
  }, []);

  return (
    <div className="h-full w-full bg-slate-900 relative">
      {/* 主摄像头画面 */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
        {/* RTSP 视频画面 */}
        {isStreaming ? (
          <img 
            ref={imgRef}
            alt="RTSP 视频流"
            className="w-full h-full object-contain"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center flex-col gap-4">
            <Video className="size-32 text-slate-700/50" />
            {streamError && (
              <div className="text-red-400 text-sm font-mono bg-red-950/50 px-4 py-2 rounded-lg border border-red-500/30">
                {streamError}
              </div>
            )}
            {!streamError && (
              <div className="text-slate-500 text-sm font-mono">正在连接视频流...</div>
            )}
          </div>
        )}

        {/* AI检测框示例 */}
        <div className="absolute top-1/4 left-1/3 w-48 h-64 border-2 border-red-500 shadow-lg shadow-red-500/30 animate-pulse">
          <div className="bg-gradient-to-r from-red-600 to-red-500 text-white px-3 py-1.5 text-sm font-mono -mt-8 shadow-lg">
            ⚠️ 人员检测
          </div>
          <div className="absolute top-2 right-2 bg-red-500/90 backdrop-blur-sm text-white px-2 py-1 rounded text-xs font-mono">
            95%
          </div>
        </div>

        <div className="absolute top-1/2 right-1/4 w-32 h-32 border-2 border-green-500 shadow-lg shadow-green-500/30">
          <div className="bg-gradient-to-r from-green-600 to-green-500 text-white px-3 py-1.5 text-sm font-mono -mt-8 shadow-lg">
            🎯 设备追踪
          </div>
          <div className="absolute top-2 right-2 bg-green-500/90 backdrop-blur-sm text-white px-2 py-1 rounded text-xs font-mono">
            87%
          </div>
        </div>

        {/* 网格线 */}
        <svg className="absolute inset-0 w-full h-full opacity-10 pointer-events-none">
          <defs>
            <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="currentColor" strokeWidth="0.5" className="text-cyan-400"/>
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#grid)" />
        </svg>

        {/* 十字准线 */}
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
          <Crosshair className="size-16 text-cyan-500/30" />
        </div>

        {/* 角落装饰 */}
        <div className="absolute top-4 left-4 w-12 h-12 border-l-2 border-t-2 border-cyan-500/50"></div>
        <div className="absolute top-4 right-4 w-12 h-12 border-r-2 border-t-2 border-cyan-500/50"></div>
        <div className="absolute bottom-4 left-4 w-12 h-12 border-l-2 border-b-2 border-cyan-500/50"></div>
        <div className="absolute bottom-4 right-4 w-12 h-12 border-r-2 border-b-2 border-cyan-500/50"></div>
      </div>

      {/* 状态信息叠加层 */}
      <div className="absolute top-0 left-0 right-0 p-6 flex justify-between items-start">
        {/* 左侧信息 */}
        <div className="space-y-3">
          {/* 摄像头信息 */}
          <div className="bg-slate-950/90 backdrop-blur-md border-2 border-cyan-500/30 rounded-lg px-4 py-3 shadow-xl">
            <div className="flex items-center gap-3">
              <div className={`size-3 rounded-full shadow-lg ${isStreaming ? 'bg-red-500 animate-pulse shadow-red-500/50' : 'bg-slate-500 shadow-slate-500/50'}`}></div>
              <span className="text-cyan-400 font-mono">主摄像头 {isStreaming ? '(直播中)' : '(离线)'}</span>
            </div>
          </div>

          {/* 运动方向 */}
          <div className="bg-slate-950/90 backdrop-blur-md border-2 border-cyan-500/30 rounded-lg px-4 py-3 shadow-xl">
            <div className="flex items-center gap-3">
              <div className={`size-3 rounded-full shadow-lg ${directionColors[direction]}`}></div>
              <span className="text-slate-300 font-mono">方向: </span>
              <span className="text-cyan-400 font-mono">{directionLabels[direction]}</span>
            </div>
          </div>

          {/* AI状态 */}
          <div className="bg-slate-950/90 backdrop-blur-md border-2 border-green-500/30 rounded-lg px-4 py-3 shadow-xl">
            <div className="flex items-center gap-3">
              <Shield className="size-5 text-green-500 animate-pulse" />
              <span className="text-slate-300 font-mono">AI追踪: </span>
              <span className="text-green-400 font-mono">激活</span>
            </div>
          </div>
        </div>

        {/* 右侧检测统计 - 移除时间显示 */}
        <div className="bg-slate-950/90 backdrop-blur-md border-2 border-cyan-500/30 rounded-lg px-4 py-3 space-y-2 shadow-xl">
          <div className="text-cyan-400 text-sm font-mono mb-2">实时统计</div>
          <div className="flex items-center gap-3 text-sm">
            <div className="size-2 bg-green-500 rounded-full shadow-lg shadow-green-500/50"></div>
            <span className="text-slate-400 font-mono">目标:</span>
            <span className="text-green-400 font-mono">2</span>
          </div>
          <div className="flex items-center gap-3 text-sm">
            <div className="size-2 bg-red-500 rounded-full shadow-lg shadow-red-500/50"></div>
            <span className="text-slate-400 font-mono">警告:</span>
            <span className="text-red-400 font-mono">1</span>
          </div>
        </div>
      </div>

      {/* 底部信息栏 */}
      <div className="absolute bottom-0 left-0 right-0 p-6">
        <div className="bg-slate-950/90 backdrop-blur-md border-2 border-cyan-500/30 rounded-lg px-6 py-3 shadow-xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-8">
              <div className="flex items-center gap-2">
                <span className="text-slate-400 font-mono">分辨率:</span>
                <span className="text-cyan-400 font-mono">1920x1080</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-slate-400 font-mono">帧率:</span>
                <span className="text-cyan-400 font-mono">{fps} FPS</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-slate-400 font-mono">总帧数:</span>
                <span className="text-cyan-400 font-mono">{frameCount}</span>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className={`size-2 rounded-full shadow-lg ${isStreaming ? 'bg-green-500 animate-pulse shadow-green-500/50' : 'bg-yellow-500 animate-pulse shadow-yellow-500/50'}`}></div>
              <span className={`font-mono ${isStreaming ? 'text-green-400' : 'text-yellow-400'}`}>
                {isStreaming ? '系统运行正常' : '等待视频流连接'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}