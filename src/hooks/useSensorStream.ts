/**
 * useSensorStream Hook
 * 管理WebSocket连接，订阅实时传感器数据流
 * Requirements: 3.1, 3.2, 5.2, 6.1, 6.2, 6.4, 6.5, 8.2
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import type { 
  SensorData, 
  MotionCommand, 
  ConnectionStatus, 
  SensorStreamMessage 
} from '../types/sensor';

/**
 * Hook配置选项
 */
interface UseSensorStreamOptions {
  autoConnect?: boolean;  // 默认true，组件挂载时自动连接
  reconnectInterval?: number;  // 初始重连间隔（毫秒）
  maxReconnectInterval?: number;  // 最大重连间隔（毫秒）
  maxReconnectAttempts?: number;  // 最大重连次数
  delayThreshold?: number;  // 延迟警告阈值（毫秒）
  websocketUrl?: string;  // WebSocket URL
}

/**
 * Hook返回值
 */
interface UseSensorStreamReturn {
  // 状态
  isConnected: boolean;
  connectionStatus: ConnectionStatus;
  sensorData: SensorData | null;
  motionCommand: MotionCommand | null;
  error: string | null;
  lastUpdateTime: Date | null;
  isDelayed: boolean;
}

/**
 * 默认配置
 */
const DEFAULT_OPTIONS: Required<UseSensorStreamOptions> = {
  autoConnect: true,
  reconnectInterval: 1000,
  maxReconnectInterval: 30000,
  maxReconnectAttempts: 10,
  delayThreshold: 2000,
  // 使用 127.0.0.1 而不是 localhost 以避免 IPv6 问题
  websocketUrl: 'ws://127.0.0.1:8000/api/sensor/stream',
};

/**
 * useSensorStream Hook
 * 
 * 自动管理WebSocket连接生命周期：
 * - 组件挂载时自动连接
 * - 组件卸载时自动断开连接和清理资源
 * - 实现自动重连机制（指数退避）
 * - 实现延迟检测（2秒无数据显示警告）
 */
export function useSensorStream(options?: UseSensorStreamOptions): UseSensorStreamReturn {
  const opts = { ...DEFAULT_OPTIONS, ...options };
  
  // 状态管理
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('disconnected');
  const [sensorData, setSensorData] = useState<SensorData | null>(null);
  const [motionCommand, setMotionCommand] = useState<MotionCommand | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdateTime, setLastUpdateTime] = useState<Date | null>(null);
  const [isDelayed, setIsDelayed] = useState(false);
  
  // Refs for WebSocket and timers
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const delayCheckIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const currentReconnectIntervalRef = useRef(opts.reconnectInterval);
  const isMountedRef = useRef(true);
  
  /**
   * 清理所有定时器
   */
  const clearTimers = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (delayCheckIntervalRef.current) {
      clearInterval(delayCheckIntervalRef.current);
      delayCheckIntervalRef.current = null;
    }
  }, []);
  
  // 使用 ref 来存储 lastUpdateTime，避免在 callback 中依赖它
  const lastUpdateTimeRef = useRef<Date | null>(null);
  
  /**
   * 启动延迟检测
   * 每秒检查一次，如果超过阈值则显示警告
   */
  const startDelayCheck = useCallback(() => {
    // 清除现有的检查
    if (delayCheckIntervalRef.current) {
      clearInterval(delayCheckIntervalRef.current);
    }
    
    delayCheckIntervalRef.current = setInterval(() => {
      if (!isMountedRef.current) return;
      
      if (lastUpdateTimeRef.current) {
        const timeSinceLastUpdate = Date.now() - lastUpdateTimeRef.current.getTime();
        if (timeSinceLastUpdate >= opts.delayThreshold) {
          setIsDelayed(true);
        } else {
          setIsDelayed(false);
        }
      }
    }, 1000);
  }, [opts.delayThreshold]);
  
  /**
   * 解析WebSocket消息
   */
  const parseMessage = useCallback((message: SensorStreamMessage) => {
    if (!isMountedRef.current) return;
    
    const now = new Date();
    lastUpdateTimeRef.current = now;  // 更新 ref
    setLastUpdateTime(now);  // 更新 state
    setIsDelayed(false);  // 收到数据，清除延迟警告
    
    if (message.type === 'sensor_data') {
      // 解析传感器数据
      const { acceleration, angularVelocity, angles, temperature, battery } = message.data;
      
      if (acceleration && angularVelocity && angles) {
        setSensorData({
          acceleration,
          angularVelocity,
          angles,
          temperature: temperature ?? 0,
          battery: battery ?? 0,
          timestamp: message.timestamp,
        });
      }
    } else if (message.type === 'motion_command') {
      // 解析运动指令
      const { command, intensity, angularIntensity, rawDirection, isMotionStart } = message.data;
      
      if (command && intensity !== undefined && angularIntensity !== undefined) {
        setMotionCommand({
          command: command as MotionCommand['command'],
          intensity,
          angularIntensity,
          rawDirection: rawDirection ?? '',
          isMotionStart: isMotionStart ?? false,
          timestamp: message.timestamp,
        });
      }
    } else if (message.type === 'error') {
      // 处理错误消息
      setError(message.data.error ?? 'Unknown error');
    }
  }, []);
  
  /**
   * 连接WebSocket
   */
  const connect = useCallback(() => {
    if (!isMountedRef.current) return;
    
    // 如果已经连接或正在连接，不重复连接
    if (wsRef.current?.readyState === WebSocket.OPEN || 
        wsRef.current?.readyState === WebSocket.CONNECTING) {
      return;
    }
    
    setConnectionStatus('connecting');
    setError(null);
    
    try {
      const ws = new WebSocket(opts.websocketUrl);
      wsRef.current = ws;
      
      ws.onopen = () => {
        if (!isMountedRef.current) return;
        
        setConnectionStatus('connected');
        setError(null);
        reconnectAttemptsRef.current = 0;
        currentReconnectIntervalRef.current = opts.reconnectInterval;
        
        // 启动延迟检测
        startDelayCheck();
      };
      
      ws.onmessage = (event) => {
        if (!isMountedRef.current) return;
        
        try {
          const message: SensorStreamMessage = JSON.parse(event.data);
          parseMessage(message);
        } catch (err) {
          console.error('[useSensorStream] Failed to parse WebSocket message:', err);
          setError('数据解析失败');
        }
      };
      
      ws.onerror = (event) => {
        if (!isMountedRef.current) return;
        
        console.error('[useSensorStream] ✗ WebSocket error:', event);
        console.error('[useSensorStream] WebSocket URL:', opts.websocketUrl);
        console.error('[useSensorStream] WebSocket readyState:', ws.readyState);
        console.error('[useSensorStream] Event type:', event.type);
        console.error('[useSensorStream] Event target:', event.target);
        
        setConnectionStatus('error');
        setError(`连接错误: 无法连接到 ${opts.websocketUrl}`);
      };
      
      ws.onclose = () => {
        if (!isMountedRef.current) return;
        
        setConnectionStatus('disconnected');
        
        // 尝试自动重连
        if (reconnectAttemptsRef.current < opts.maxReconnectAttempts) {
          reconnectAttemptsRef.current++;
          
          // 指数退避
          const delay = Math.min(
            currentReconnectIntervalRef.current,
            opts.maxReconnectInterval
          );
          currentReconnectIntervalRef.current *= 2;
          
          reconnectTimeoutRef.current = setTimeout(() => {
            if (isMountedRef.current) {
              connect();
            }
          }, delay);
        } else {
          setError('连接失败，已达到最大重连次数');
        }
      };
    } catch (err) {
      console.error('[useSensorStream] ✗ Failed to create WebSocket:', err);
      setConnectionStatus('error');
      setError('无法创建连接');
    }
  }, [opts, parseMessage, startDelayCheck]);
  
  /**
   * 断开WebSocket连接
   */
  const disconnect = useCallback(() => {
    clearTimers();
    
    if (wsRef.current) {
      // 设置为null以防止onclose触发重连
      const ws = wsRef.current;
      wsRef.current = null;
      
      if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) {
        ws.close();
      }
    }
    
    setConnectionStatus('disconnected');
    reconnectAttemptsRef.current = 0;
    currentReconnectIntervalRef.current = opts.reconnectInterval;
  }, [clearTimers, opts.reconnectInterval]);
  
  /**
   * 组件挂载时自动连接
   * 组件卸载时自动断开连接和清理资源
   */
  useEffect(() => {
    isMountedRef.current = true;
    
    if (opts.autoConnect) {
      connect();
    }
    
    // 清理函数
    return () => {
      isMountedRef.current = false;
      disconnect();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [opts.autoConnect]); // 只依赖 autoConnect，避免重复连接
  
  /**
   * 启动延迟检测
   */
  useEffect(() => {
    if (connectionStatus === 'connected') {
      startDelayCheck();
    }
    
    return () => {
      if (delayCheckIntervalRef.current) {
        clearInterval(delayCheckIntervalRef.current);
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [connectionStatus]); // 只依赖 connectionStatus
  
  return {
    isConnected: connectionStatus === 'connected',
    connectionStatus,
    sensorData,
    motionCommand,
    error,
    lastUpdateTime,
    isDelayed,
  };
}
