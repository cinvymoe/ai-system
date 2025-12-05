/**
 * TypeScript type definitions for sensor data display
 * Requirements: 1.2, 1.3, 1.4, 2.1, 6.3
 */

/**
 * 传感器数据接口
 * 包含加速度、角速度、角度等原始传感器数据
 */
export interface SensorData {
  acceleration: {
    x: number;  // g
    y: number;  // g
    z: number;  // g
  };
  angularVelocity: {
    x: number;  // °/s
    y: number;  // °/s
    z: number;  // °/s
  };
  angles: {
    x: number;  // °
    y: number;  // °
    z: number;  // °
  };
  temperature: number;  // °C
  battery: number;  // %
  timestamp: string;
}

/**
 * 运动指令接口
 * 包含处理后的运动方向、强度等信息
 */
export interface MotionCommand {
  command: 'forward' | 'backward' | 'turn_left' | 'turn_right' | 'stationary';
  intensity: number;  // 线性运动强度
  angularIntensity: number;  // 角度运动强度
  rawDirection: string;  // 原始方向字符串
  isMotionStart: boolean;  // 是否是运动开始
  timestamp: string;
}

/**
 * WebSocket消息接口
 * 定义前后端通信的消息格式
 */
export interface SensorStreamMessage {
  type: 'sensor_data' | 'motion_command' | 'error';
  timestamp: string;
  data: {
    // sensor_data类型
    acceleration?: { x: number; y: number; z: number };
    angularVelocity?: { x: number; y: number; z: number };
    angles?: { x: number; y: number; z: number };
    temperature?: number;
    battery?: number;
    
    // motion_command类型
    command?: string;
    intensity?: number;
    angularIntensity?: number;
    rawDirection?: string;
    isMotionStart?: boolean;
    
    // error类型
    error?: string;
  };
}

/**
 * 连接状态类型
 * 表示WebSocket连接的当前状态
 */
export type ConnectionStatus = 'disconnected' | 'connecting' | 'connected' | 'error';
