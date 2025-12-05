/**
 * Electron 预加载脚本
 * 在渲染进程加载前执行，通过 contextBridge 安全地暴露 API
 * 需求: 3.1, 3.2, 3.5, 7.1
 */

import { contextBridge, ipcRenderer } from 'electron';
import type { ElectronAPI, CameraAPI } from './types';

/**
 * 通过 contextBridge 暴露安全的 API 给渲染进程
 * 需求: 3.2, 3.5
 */
const electronAPI: ElectronAPI = {
  /**
   * Ping 测试方法 - 验证 IPC 通信是否正常工作
   * 需求: 7.1, 7.4
   */
  ping: (): Promise<string> => {
    return ipcRenderer.invoke('ping');
  },

  /**
   * 发送单向 IPC 消息到主进程
   * 需求: 7.1, 7.2
   */
  send: (channel: string, data: any): void => {
    // 验证频道名称，防止恶意调用
    if (typeof channel !== 'string' || channel.trim() === '') {
      console.error('Invalid IPC channel name');
      return;
    }
    ipcRenderer.send(channel, data);
  },

  /**
   * 监听来自主进程的 IPC 消息
   * 需求: 7.1, 7.2
   */
  on: (channel: string, callback: (data: any) => void): (() => void) => {
    // 验证频道名称
    if (typeof channel !== 'string' || channel.trim() === '') {
      console.error('Invalid IPC channel name');
      return () => {};
    }

    // 验证回调函数
    if (typeof callback !== 'function') {
      console.error('Callback must be a function');
      return () => {};
    }

    // 创建包装函数来处理 IPC 事件
    const subscription = (_event: Electron.IpcRendererEvent, data: any) => {
      callback(data);
    };

    // 注册监听器
    ipcRenderer.on(channel, subscription);

    // 返回取消监听的函数
    return () => {
      ipcRenderer.removeListener(channel, subscription);
    };
  },

  /**
   * 系统平台信息
   * 需求: 3.5
   */
  platform: process.platform,

  /**
   * Electron 版本信息
   * 需求: 3.5
   */
  version: process.versions.electron || 'unknown',
};

/**
 * Camera API - 摄像头数据库操作接口
 * 需求: 8.1
 */
const cameraAPI: CameraAPI = {
  /**
   * Get all cameras
   * 需求: 8.1
   */
  getAll: (): Promise<any> => {
    return ipcRenderer.invoke('camera:getAll');
  },

  /**
   * Get camera by ID
   * 需求: 8.1
   */
  getById: (cameraId: string): Promise<any> => {
    return ipcRenderer.invoke('camera:getById', cameraId);
  },

  /**
   * Get cameras by direction
   * 需求: 8.1
   */
  getByDirection: (direction: string): Promise<any> => {
    return ipcRenderer.invoke('camera:getByDirection', direction);
  },

  /**
   * Create new camera
   * 需求: 8.1
   */
  create: (cameraData: any): Promise<any> => {
    return ipcRenderer.invoke('camera:create', cameraData);
  },

  /**
   * Update camera
   * 需求: 8.1
   */
  update: (cameraId: string, updates: any): Promise<any> => {
    return ipcRenderer.invoke('camera:update', cameraId, updates);
  },

  /**
   * Delete camera
   * 需求: 8.1
   */
  delete: (cameraId: string): Promise<any> => {
    return ipcRenderer.invoke('camera:delete', cameraId);
  },

  /**
   * Update camera status
   * 需求: 8.1
   */
  updateStatus: (cameraId: string, status: string): Promise<any> => {
    return ipcRenderer.invoke('camera:updateStatus', cameraId, status);
  },
};

/**
 * 使用 contextBridge 安全地暴露 API
 * 这确保了渲染进程无法直接访问 Node.js 或 Electron 的完整 API
 * 需求: 3.1, 3.2, 8.1
 */
contextBridge.exposeInMainWorld('electronAPI', electronAPI);
contextBridge.exposeInMainWorld('cameraAPI', cameraAPI);

// 日志记录（仅在开发模式）
if (process.env.NODE_ENV === 'development') {
  console.log('Preload script loaded successfully');
  console.log('Platform:', electronAPI.platform);
  console.log('Electron version:', electronAPI.version);
}
