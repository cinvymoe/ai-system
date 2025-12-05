/**
 * TypeScript 类型定义文件
 * 定义 Electron API 接口和相关类型
 * 需求: 3.2, 3.5, 7.1
 */

/**
 * 暴露给渲染进程的 Electron API 接口
 */
export interface ElectronAPI {
  /**
   * Ping 测试方法 - 用于验证 IPC 通信
   * 需求: 7.1, 7.4
   * @returns Promise<string> 返回 'pong'
   */
  ping: () => Promise<string>;

  /**
   * 发送 IPC 消息到主进程（单向通信）
   * 需求: 7.1, 7.2
   * @param channel 通信频道名称
   * @param data 要发送的数据
   */
  send: (channel: string, data: any) => void;

  /**
   * 监听来自主进程的 IPC 消息
   * 需求: 7.1, 7.2
   * @param channel 通信频道名称
   * @param callback 接收消息的回调函数
   * @returns 返回取消监听的函数
   */
  on: (channel: string, callback: (data: any) => void) => () => void;

  /**
   * 系统平台信息
   * 需求: 3.5
   */
  platform: string;

  /**
   * Electron 版本信息
   * 需求: 3.5
   */
  version: string;
}

/**
 * Camera API 接口
 * 需求: 8.1
 */
export interface CameraAPI {
  /**
   * Get all cameras
   */
  getAll: () => Promise<IPCResponse>;

  /**
   * Get camera by ID
   */
  getById: (cameraId: string) => Promise<IPCResponse>;

  /**
   * Get cameras by direction
   */
  getByDirection: (direction: string) => Promise<IPCResponse>;

  /**
   * Create new camera
   */
  create: (cameraData: any) => Promise<IPCResponse>;

  /**
   * Update camera
   */
  update: (cameraId: string, updates: any) => Promise<IPCResponse>;

  /**
   * Delete camera
   */
  delete: (cameraId: string) => Promise<IPCResponse>;

  /**
   * Update camera status
   */
  updateStatus: (cameraId: string, status: string) => Promise<IPCResponse>;
}

/**
 * 扩展 Window 接口，添加 electronAPI 和 cameraAPI
 */
declare global {
  interface Window {
    electronAPI: ElectronAPI;
    cameraAPI: CameraAPI;
  }
}

/**
 * IPC 消息格式
 */
export interface IPCMessage<T = any> {
  channel: string;
  data: T;
  timestamp: number;
}

/**
 * IPC 响应格式
 */
export interface IPCResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
}
