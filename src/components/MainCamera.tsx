import { useEffect, useRef, useState } from 'react';
import { Video, Crosshair } from 'lucide-react';
import { Direction } from '../App';

interface MainCameraProps {
  direction: Direction;
  activeCameraId: string;
  onAlert?: (alert: { type: 'intrusion' | 'tracking' | 'system'; message: string }) => void;
}

interface CameraInfo {
  id: string;
  name: string;
  url: string;
  status: string;
  directions: string[];
}

interface BrokerMessage {
  type: string;
  message_id: string;
  timestamp: string;
  data: any;
  cameras: CameraInfo[];
  priority: number;
  remaining_time: number;
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

const BROKER_WS_URL = 'ws://127.0.0.1:8000/api/broker/stream';
const RTSP_API_BASE = 'http://127.0.0.1:8000/rtsp';
const RTSP_WS_BASE = 'ws://127.0.0.1:8000/rtsp';
const PERSON_DETECTION_WS_BASE = 'ws://127.0.0.1:8000/api/person-detection';

// 多摄像头流状态
interface CameraStream {
  camera: CameraInfo;
  ws: WebSocket | null;
  imgRef: React.RefObject<HTMLImageElement>;
  isStreaming: boolean;
  error: string | null;
}

export function MainCamera({ direction: propDirection, onAlert }: MainCameraProps) {
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamError, setStreamError] = useState<string | null>(null);
  const [frameCount, setFrameCount] = useState(0);
  const [fps, setFps] = useState(0);
  const [currentCamera, setCurrentCamera] = useState<CameraInfo | null>(null);
  const [activeCameras, setActiveCameras] = useState<CameraInfo[]>([]);
  const [brokerConnected, setBrokerConnected] = useState(false);
  const [direction, setDirection] = useState<Direction>(propDirection);
  const [cameraStreams, setCameraStreams] = useState<Map<string, CameraStream>>(new Map());
  const [currentAngle, setCurrentAngle] = useState<number | null>(null);
  const [isAlertMode, setIsAlertMode] = useState(false); // AI报警模式状态
  const [alertCamera, setAlertCamera] = useState<CameraInfo | null>(null); // 报警摄像头

  
  const imgRef = useRef<HTMLImageElement>(null);
  const rtspWsRef = useRef<WebSocket | null>(null);
  const brokerWsRef = useRef<WebSocket | null>(null);
  const fpsCounterRef = useRef({ count: 0, lastTime: Date.now() });
  const currentStreamIdRef = useRef<string | null>(null);
  const currentCameraIdRef = useRef<string | null>(null); // 跟踪当前摄像头 ID
  const pendingCameraRef = useRef<CameraInfo | null>(null); // 保存待恢复的摄像头
  const cameraStreamsRef = useRef<Map<string, CameraStream>>(new Map());
  const alertWsRef = useRef<WebSocket | null>(null); // AI报警WebSocket连接
  const isAlertModeRef = useRef<boolean>(false); // 跟踪AI报警模式状态（用于闭包中访问最新值）
  const alertCameraRef = useRef<CameraInfo | null>(null); // 跟踪报警摄像头（用于闭包中访问最新值）

  // 启动多个摄像头流
  const startMultipleStreams = async (cameras: CameraInfo[]) => {
    console.log(`启动多摄像头模式，摄像头数量: ${cameras.length}`);
    
    // 最多显示4个摄像头
    const camerasToShow = cameras.slice(0, 4);
    
    // 检查摄像头是否未变化
    const currentCameraIds = Array.from(cameraStreamsRef.current.keys()).sort().join(',');
    const newCameraIds = camerasToShow.map(c => c.id).sort().join(',');
    
    if (currentCameraIds === newCameraIds && cameraStreamsRef.current.size > 0) {
      console.log('多摄像头未变化，保持当前流');
      return;
    }
    
    console.log(`摄像头变化: [${currentCameraIds}] -> [${newCameraIds}]`);
    
    // 停止旧的流
    await stopMultipleStreams();
    
    const newStreams = new Map<string, CameraStream>();
    
    for (const camera of camerasToShow) {
      const imgRef = { current: null } as React.RefObject<HTMLImageElement>;
      const stream: CameraStream = {
        camera,
        ws: null,
        imgRef,
        isStreaming: false,
        error: null
      };
      
      newStreams.set(camera.id, stream);
      
      // 启动流
      try {
        const streamId = `${camera.id}`;
        const response = await fetch(`${RTSP_API_BASE}/streams/start`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            stream_id: streamId,
            rtsp_url: camera.url
          })
        });

        if (response.ok) {
          console.log(`多摄像头流启动成功: ${camera.name}`);
          connectMultiCameraWebSocket(camera.id, streamId, stream);
        }
      } catch (error) {
        console.error(`启动摄像头 ${camera.name} 失败:`, error);
        stream.error = '启动失败';
      }
    }
    
    cameraStreamsRef.current = newStreams;
    setCameraStreams(newStreams);
  };

  // 连接多摄像头 WebSocket
  const connectMultiCameraWebSocket = (cameraId: string, streamId: string, stream: CameraStream) => {
    const ws = new WebSocket(`${RTSP_WS_BASE}/ws/${streamId}`);
    stream.ws = ws;

    ws.onopen = () => {
      console.log(`多摄像头 WebSocket 已连接: ${stream.camera.name}`);
      stream.isStreaming = true;
      setCameraStreams(new Map(cameraStreamsRef.current));
    };

    ws.onmessage = (event) => {
      if (event.data instanceof Blob && stream.imgRef.current) {
        const url = URL.createObjectURL(event.data);
        
        if (stream.imgRef.current.src.startsWith('blob:')) {
          URL.revokeObjectURL(stream.imgRef.current.src);
        }
        stream.imgRef.current.src = url;
      }
    };

    ws.onerror = () => {
      stream.error = 'WebSocket 连接错误';
      stream.isStreaming = false;
      setCameraStreams(new Map(cameraStreamsRef.current));
    };

    ws.onclose = () => {
      stream.isStreaming = false;
      setCameraStreams(new Map(cameraStreamsRef.current));
    };
  };

  // 停止所有多摄像头流
  const stopMultipleStreams = async () => {
    for (const [cameraId, stream] of cameraStreamsRef.current.entries()) {
      if (stream.ws) {
        stream.ws.close();
      }
      
      try {
        await fetch(`${RTSP_API_BASE}/streams/stop/${cameraId}`, {
          method: 'POST'
        });
      } catch (error) {
        console.error(`停止摄像头 ${cameraId} 失败:`, error);
      }
    }
    
    cameraStreamsRef.current.clear();
    setCameraStreams(new Map());
  };

  // 停止AI报警流
  const stopAlertStream = async () => {
    if (alertWsRef.current) {
      alertWsRef.current.close();
      alertWsRef.current = null;
    }
    
    isAlertModeRef.current = false; // 同步更新 ref
    alertCameraRef.current = null;
    setIsAlertMode(false);
    setAlertCamera(null);
    setIsStreaming(false);
    setFrameCount(0);
    setFps(0);
    console.log('AI报警流已停止');
  };

  // 启动AI报警流
  const startAlertStream = async (camera: CameraInfo) => {
    // 使用 ref 检查是否已经是相同摄像头的AI报警流（避免闭包问题）
    if (isAlertModeRef.current && alertCameraRef.current?.id === camera.id && alertWsRef.current?.readyState === WebSocket.OPEN) {
      console.log(`AI报警流已在运行: ${camera.name} (${camera.id})`);
      return;
    }
    
    // 只有在不同摄像头或连接断开时才停止现有报警流
    if (isAlertModeRef.current && (alertCameraRef.current?.id !== camera.id || alertWsRef.current?.readyState !== WebSocket.OPEN)) {
      await stopAlertStream();
    }
    
    console.log(`启动AI报警流: ${camera.name} (${camera.id})`);

    // 同步更新 ref（在状态更新之前）
    alertCameraRef.current = camera;
    setAlertCamera(camera);
    
    try {
      // 直接连接人员检测WebSocket端点
      const ws = new WebSocket(`${PERSON_DETECTION_WS_BASE}/ws/${camera.id}`);
      alertWsRef.current = ws;

      ws.onopen = () => {
        console.log(`AI报警WebSocket已连接: ${camera.name}`);
        setIsStreaming(true);
      };

      ws.onmessage = (event) => {
        if (event.data instanceof Blob && imgRef.current) {
          // 接收到带有人员检测标注的图像帧
          const url = URL.createObjectURL(event.data);
          
          if (imgRef.current.src.startsWith('blob:')) {
            URL.revokeObjectURL(imgRef.current.src);
          }
          imgRef.current.src = url;
          
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
          // JSON 消息 - 检测信息
          try {
            const msg = JSON.parse(event.data);
            if (msg.type === 'detection') {
              console.log(`检测信息: 人数=${msg.person_count}, 时间=${msg.timestamp}`);
            } else if (msg.type === 'error') {
              console.error('AI报警流错误:', msg.message);
            }
          } catch (e) {
            console.error('解析AI报警消息失败:', e);
          }
        }
      };

      ws.onerror = (error) => {
        console.error('AI报警WebSocket错误:', error);
      };

      ws.onclose = () => {
        console.log('AI报警WebSocket已断开');
        setIsStreaming(false);
      };
      
    } catch (error) {
      console.error('启动AI报警流失败:', error);
      setAlertCamera(null);
    }
  };

  // 停止当前 RTSP 流
  const stopCurrentStream = async () => {
    // 关闭 RTSP WebSocket
    if (rtspWsRef.current) {
      rtspWsRef.current.close();
      rtspWsRef.current = null;
    }

    // 停止后端流
    if (currentStreamIdRef.current) {
      try {
        await fetch(`${RTSP_API_BASE}/streams/stop/${currentStreamIdRef.current}`, {
          method: 'POST'
        });
        console.log(`RTSP 流已停止: ${currentStreamIdRef.current}`);
      } catch (error) {
        console.error('停止 RTSP 流失败:', error);
      }
      currentStreamIdRef.current = null;
    }

    currentCameraIdRef.current = null; // 清除摄像头 ID ref
    setIsStreaming(false);
    setFrameCount(0);
    setFps(0);
  };

  // 启动 RTSP 流
  const startStream = async (camera: CameraInfo) => {
    try {
      // 先停止当前流
      await stopCurrentStream();

      const streamId = `${camera.id}`;
      currentStreamIdRef.current = streamId;

      const response = await fetch(`${RTSP_API_BASE}/streams/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          stream_id: streamId,
          rtsp_url: camera.url
        })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || '启动流失败');
      }

      console.log(`RTSP 流启动成功: ${camera.name} (${camera.url})`);
      setCurrentCamera(camera);
      currentCameraIdRef.current = camera.id; // 更新 ref
      connectRtspWebSocket(streamId);
    } catch (error) {
      console.error('启动 RTSP 流失败:', error);
      setStreamError(error instanceof Error ? error.message : '启动流失败');
    }
  };

  // 连接 RTSP WebSocket
  const connectRtspWebSocket = (streamId: string) => {
    const ws = new WebSocket(`${RTSP_WS_BASE}/ws/${streamId}`);
    rtspWsRef.current = ws;

    ws.onopen = () => {
      console.log('RTSP WebSocket 已连接');
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
      console.error('RTSP WebSocket 错误:', error);
      setStreamError('WebSocket 连接错误');
      setIsStreaming(false);
    };

    ws.onclose = () => {
      console.log('RTSP WebSocket 已断开');
      setIsStreaming(false);
    };
  };



  // 组件挂载时连接 Broker WebSocket，卸载时清理
  useEffect(() => {
    let isUnmounting = false;

    // 修改 connectBrokerWebSocket 以支持取消重连
    const connectWithCleanup = () => {
      const ws = new WebSocket(BROKER_WS_URL);
      brokerWsRef.current = ws;

      ws.onopen = () => {
        console.log('Broker WebSocket 已连接');
        setBrokerConnected(true);
      };

      ws.onmessage = async (event) => {
        try {
          const message: BrokerMessage = JSON.parse(event.data);
          console.log('收到 Broker 消息:', message);

          // 从 data.command 解析方向
          if (message.data && message.data.command) {
            const command = message.data.command;
            let newDirection: Direction = 'idle';
            
            // 映射 command 到 Direction
            if (command === 'forward') {
              newDirection = 'forward';
            } else if (command === 'backward') {
              newDirection = 'backward';
            } else if (command === 'turn_left') {
              newDirection = 'left';
            } else if (command === 'turn_right') {
              newDirection = 'right';
            } else if (command === 'stationary') {
              newDirection = 'idle';
            }
            
            console.log(`方向更新: ${command} -> ${newDirection}`);
            setDirection(newDirection);
            // 收到方向消息时清除角度，让方向文字覆盖显示
            setCurrentAngle(null);
          }

          // 处理 AI 警报
          if (message.type === 'ai_alert') {
            console.log('收到 AI 警报:', message);
            if (message.data && onAlert) {
              const { alert_type, camera_name, person_count, confidence, camera_id } = message.data;
              
              // 发送警报到父组件，只弹出AlertPanel
              let alertMessage = '';
              if (alert_type === 'person_detected') {
                alertMessage = `检测到 ${person_count} 人入侵 - 摄像头: ${camera_name || '未知'} (置信度: ${Math.round((confidence || 0) * 100)}%)`;
              } else {
                alertMessage = `AI 检测警报 - ${alert_type}`;
              }
              
              onAlert({
                type: 'intrusion',
                message: alertMessage
              });

              // 启动AI报警单画面显示 - 直接播放不需要检测摄像头
              if (camera_id) {
                console.log(`AI报警触发单画面显示: ${camera_name || camera_id}`);
                
                // 创建临时摄像头信息用于AI报警显示
                const alertCameraInfo = {
                  id: camera_id,
                  name: camera_name || `摄像头_${camera_id}`,
                  url: `rtsp://camera_${camera_id}`, // 临时URL，实际不使用
                  status: 'online',
                  directions: []
                };
                
                // 使用 ref 检查当前是否已经是相同摄像头的AI报警模式（避免闭包问题）
                if (isAlertModeRef.current && alertCameraRef.current?.id === camera_id) {
                  console.log('当前已是相同摄像头的AI报警模式，无需切换');
                  return;
                }
                
                // 停止现有流并启动AI报警流
                console.log('当前isAlertMode (ref):', isAlertModeRef.current);
                
                // 停止当前的多摄像头流
                if (cameraStreamsRef.current.size > 0) {
                  await stopMultipleStreams();
                }
                
                // 停止当前的单摄像头流
                if (currentStreamIdRef.current) {
                  await stopCurrentStream();
                }

                // 同步更新 ref（在状态更新之前，确保后续检查能立即生效）
                isAlertModeRef.current = true;
                setIsAlertMode(true);
                console.log('设置isAlertMode为true (ref已同步更新)');

                // 启动AI报警流
                startAlertStream(alertCameraInfo);
              }
            }
          } else if (message.type === 'camera_switch' || message.type === 'stream_end') {
            // 只在明确的摄像头切换或流结束消息时退出AI报警模式（使用 ref 检查）
            if (isAlertModeRef.current) {
              console.log('收到摄像头切换/流结束消息，退出报警模式:', message.type);
              await stopAlertStream();
            }
          }

          // 解析角度值
          if (message.data && typeof message.data.angle !== 'undefined') {
            const angle = parseFloat(message.data.angle);
            if (!isNaN(angle)) {
              console.log(`角度更新: ${angle}°`);
              setCurrentAngle(angle);
            }
          } else if (message.type === 'angle_value' && typeof message.data.angle !== 'undefined') {
            // 兼容 angle_value 类型消息
            const angle = parseFloat(message.data.angle);
            if (!isNaN(angle)) {
              console.log(`角度更新 (angle_value): ${angle}°`);
              setCurrentAngle(angle);
            }
          }

          if (message.type === 'current_state') {
            console.log('当前状态:', message);
          } else if (message.cameras && message.cameras.length > 0) {
            setActiveCameras(message.cameras);
            
            // 如果当前处于AI报警模式，不切换摄像头（使用 ref 检查）
            if (isAlertModeRef.current) {
              console.log('当前处于AI报警模式，不切换摄像头');
              return;
            }
            
            // 根据摄像头数量选择显示模式
            if (message.cameras.length > 1) {
              // 多摄像头模式：分四块显示
              console.log(`多摄像头模式: ${message.cameras.length} 个摄像头`);
              
              // 停止单摄像头流
              if (currentStreamIdRef.current) {
                await stopCurrentStream();
              }
              
              // 启动多摄像头流
              await startMultipleStreams(message.cameras);
            } else {
              // 单摄像头模式
              const targetCamera = message.cameras[0];
              
              if (targetCamera) {
                // 停止多摄像头流
                if (cameraStreamsRef.current.size > 0) {
                  await stopMultipleStreams();
                }
                
                // 使用 ref 进行比较，避免闭包问题
                if (currentCameraIdRef.current === targetCamera.id) {
                  console.log(`摄像头未变化，保持当前: ${targetCamera.name}`);
                  return;
                }
                
                console.log(`切换到摄像头: ${targetCamera.name} (${targetCamera.id})`);
                startStream(targetCamera);
              }
            }
          }
        } catch (error) {
          console.error('解析 Broker 消息失败:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('Broker WebSocket 错误:', error);
        setBrokerConnected(false);
      };

      ws.onclose = () => {
        console.log('Broker WebSocket 已断开');
        setBrokerConnected(false);
        
        // 只有在组件未卸载时才尝试重连
        if (!isUnmounting) {
          setTimeout(() => {
            if (!isUnmounting) {
              console.log('尝试重连 Broker WebSocket...');
              connectWithCleanup();
            }
          }, 3000);
        }
      };
    };

    connectWithCleanup();

    return () => {
      console.log('MainCamera 组件卸载，清理资源...');
      isUnmounting = true;
      
      // 清理 Broker WebSocket
      if (brokerWsRef.current) {
        brokerWsRef.current.close();
        brokerWsRef.current = null;
      }
      
      // 清理AI报警流
      stopAlertStream().catch(err => {
        console.error('清理AI报警流时出错:', err);
      });
      
      // 清理单摄像头 RTSP 流
      stopCurrentStream().catch(err => {
        console.error('清理 RTSP 流时出错:', err);
      });
      
      // 清理多摄像头流
      stopMultipleStreams().catch(err => {
        console.error('清理多摄像头流时出错:', err);
      });
    };
  }, []);

  // 页面可见性变化处理
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.hidden) {
        // 页面隐藏（切换到其他界面）
        console.log('页面隐藏，暂停视频流');
        if (currentCamera) {
          pendingCameraRef.current = currentCamera; // 保存当前摄像头
        }
        stopCurrentStream().catch(err => {
          console.error('暂停流时出错:', err);
        });
      } else {
        // 页面显示（返回到此界面）
        console.log('页面显示，恢复视频流');
        if (pendingCameraRef.current) {
          const cameraToRestore = pendingCameraRef.current;
          // 延迟一下再恢复，确保资源已释放
          setTimeout(() => {
            console.log(`恢复摄像头: ${cameraToRestore.name}`);
            startStream(cameraToRestore);
          }, 500);
        }
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [currentCamera]);

  // 清理图片 URL
  useEffect(() => {
    return () => {
      if (imgRef.current && imgRef.current.src.startsWith('blob:')) {
        URL.revokeObjectURL(imgRef.current.src);
      }
    };
  }, []);

  // 判断是否为多摄像头模式
  const isMultiCameraMode = cameraStreams.size > 1;
  
  // 判断当前显示模式
  const getDisplayMode = () => {
    if (isAlertMode) return 'alert';
    if (isMultiCameraMode) return 'multi';
    return 'single';
  };
  
  const displayMode = getDisplayMode();

  return (
    <div className="h-full w-full bg-slate-900 relative">
      {/* 主摄像头画面 */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
        {displayMode === 'alert' ? (
          // AI报警单画面显示
          <>
            {alertCamera && (
              <img 
                ref={imgRef}
                alt={`AI报警 - ${alertCamera.name}`}
                className="w-full h-full object-contain"
              />
            )}
            
            {/* AI报警模式标识 */}
            <div className="absolute top-4 left-1/2 transform -translate-x-1/2 bg-red-950/90 backdrop-blur-md border-2 border-red-500/50 rounded-lg px-6 py-3 shadow-xl">
              <div className="flex items-center gap-3">
                <div className="size-3 rounded-full bg-red-500 animate-pulse shadow-lg shadow-red-500/50"></div>
                <span className="text-red-400 font-mono font-bold">AI 报警模式</span>
                {alertCamera && (
                  <span className="text-red-300 font-mono">- {alertCamera.name}</span>
                )}
              </div>
            </div>
          </>
        ) : displayMode === 'multi' ? (
          // 多摄像头网格显示（2x2）
          <div className="w-full h-full grid grid-cols-2 grid-rows-2 gap-2 p-4">
            {Array.from(cameraStreams.values()).map((stream, index) => (
              <div key={stream.camera.id} className="relative bg-slate-800 rounded-lg overflow-hidden border-2 border-slate-700">
                {stream.isStreaming ? (
                  <img 
                    ref={stream.imgRef}
                    alt={stream.camera.name}
                    className="w-full h-full object-contain"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center flex-col gap-2">
                    <Video className="size-16 text-slate-700/50" />
                    {stream.error && (
                      <div className="text-red-400 text-xs font-mono">{stream.error}</div>
                    )}
                    {!stream.error && (
                      <div className="text-slate-500 text-xs font-mono">连接中...</div>
                    )}
                  </div>
                )}
                
                {/* 摄像头标签 */}
                <div className="absolute top-2 left-2 bg-slate-950/90 backdrop-blur-sm px-3 py-1 rounded-lg border border-cyan-500/30">
                  <div className="flex items-center gap-2">
                    <div className={`size-2 rounded-full ${stream.isStreaming ? 'bg-green-500 animate-pulse' : 'bg-slate-500'}`}></div>
                    <span className="text-cyan-400 text-xs font-mono">{stream.camera.name}</span>
                  </div>
                </div>
              </div>
            ))}
            
            {/* 填充空白格子 */}
            {Array.from({ length: 4 - cameraStreams.size }).map((_, index) => (
              <div key={`empty-${index}`} className="relative bg-slate-800/50 rounded-lg border-2 border-slate-700/50 flex items-center justify-center">
                <Video className="size-16 text-slate-700/30" />
              </div>
            ))}
          </div>
        ) : (
          // 单摄像头全屏显示
          <>
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
          </>
        )}

        {/* 单摄像头模式下的装饰元素 */}
        {displayMode === 'single' && (
          <>
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
          </>
        )}


      </div>

      {/* 状态信息叠加层 */}
      <div className="absolute top-0 left-0 right-0 p-6 flex justify-between items-start">
        {/* 左侧信息 */}
        <div className="space-y-3">
          {/* Broker 连接状态 */}
          <div className="bg-slate-950/90 backdrop-blur-md border-2 border-cyan-500/30 rounded-lg px-4 py-3 shadow-xl">
            <div className="flex items-center gap-3">
              <div className={`size-3 rounded-full shadow-lg ${brokerConnected ? 'bg-green-500 animate-pulse shadow-green-500/50' : 'bg-red-500 shadow-red-500/50'}`}></div>
              <span className="text-cyan-400 font-mono">
                传感器 {brokerConnected ? '(已连接)' : '(断开)'}
              </span>
            </div>
          </div>

          {/* 运动方向和角度 */}
          <div className="bg-slate-950/90 backdrop-blur-md border-2 border-cyan-500/30 rounded-lg px-4 py-3 shadow-xl">
            <div className="flex items-center gap-3">
              <div className={`size-3 rounded-full shadow-lg ${directionColors[direction]}`}></div>
              <span className="text-slate-300 font-mono">方向: </span>
              <span className="text-cyan-400 font-mono">
                {currentAngle !== null ? `${currentAngle.toFixed(1)}°` : directionLabels[direction]}
              </span>
            </div>
          </div>
        </div>

        {/* 右侧活跃摄像头列表 */}
        <div className="bg-slate-950/90 backdrop-blur-md border-2 border-cyan-500/30 rounded-lg px-4 py-3 space-y-2 shadow-xl max-w-xs">
          <div className="text-cyan-400 text-sm font-mono mb-2">活跃摄像头</div>
          {activeCameras.length > 0 ? (
            activeCameras.map((camera) => (
              <div key={camera.id} className="flex items-center gap-2 text-sm">
                <div className={`size-2 rounded-full shadow-lg ${camera.status === 'online' ? 'bg-green-500 shadow-green-500/50' : 'bg-red-500 shadow-red-500/50'}`}></div>
                <span className="text-slate-400 font-mono truncate">{camera.name}</span>
              </div>
            ))
          ) : (
            <div className="text-slate-500 text-sm font-mono">等待数据...</div>
          )}
        </div>
      </div>

      {/* 底部信息栏 */}
      <div className="absolute bottom-0 left-0 right-0 p-6">
        <div className="bg-slate-950/90 backdrop-blur-md border-2 border-cyan-500/30 rounded-lg px-6 py-3 shadow-xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-8">
              {displayMode === 'alert' ? (
                <>
                  <div className="flex items-center gap-2">
                    <span className="text-slate-400 font-mono">显示模式:</span>
                    <span className="text-red-400 font-mono">AI报警模式</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-slate-400 font-mono">帧率:</span>
                    <span className="text-red-400 font-mono">{fps} FPS</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-slate-400 font-mono">总帧数:</span>
                    <span className="text-red-400 font-mono">{frameCount}</span>
                  </div>
                </>
              ) : displayMode === 'multi' ? (
                <>
                  <div className="flex items-center gap-2">
                    <span className="text-slate-400 font-mono">显示模式:</span>
                    <span className="text-cyan-400 font-mono">多摄像头 ({cameraStreams.size}/4)</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-slate-400 font-mono">在线:</span>
                    <span className="text-green-400 font-mono">
                      {Array.from(cameraStreams.values()).filter((s: any) => s.isStreaming).length}/{cameraStreams.size}
                    </span>
                  </div>
                </>
              ) : (
                <>
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
                </>
              )}
            </div>
            <div className="flex items-center gap-3">
              <div className={`size-2 rounded-full shadow-lg ${
                displayMode === 'alert' 
                  ? 'bg-red-500 animate-pulse shadow-red-500/50'
                  : displayMode === 'multi'
                  ? (Array.from(cameraStreams.values()).some((s: any) => s.isStreaming) ? 'bg-green-500 animate-pulse shadow-green-500/50' : 'bg-yellow-500 animate-pulse shadow-yellow-500/50')
                  : (isStreaming ? 'bg-green-500 animate-pulse shadow-green-500/50' : 'bg-yellow-500 animate-pulse shadow-yellow-500/50')
              }`}></div>
              <span className={`font-mono ${
                displayMode === 'alert'
                  ? 'text-red-400'
                  : displayMode === 'multi'
                  ? (Array.from(cameraStreams.values()).some((s: any) => s.isStreaming) ? 'text-green-400' : 'text-yellow-400')
                  : (isStreaming ? 'text-green-400' : 'text-yellow-400')
              }`}>
                {displayMode === 'alert'
                  ? 'AI报警监控中'
                  : displayMode === 'multi'
                  ? (Array.from(cameraStreams.values()).some((s: any) => s.isStreaming) ? '多摄像头运行中' : '等待连接')
                  : (isStreaming ? '系统运行正常' : '等待视频流连接')
                }
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}