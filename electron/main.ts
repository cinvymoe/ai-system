import { app, BrowserWindow, ipcMain } from 'electron';
import * as path from 'path';
import axios, { AxiosError } from 'axios';
import { IPCResponse } from './types';

// 禁用 GPU 加速以支持 ARM 设备
// app.disableHardwareAcceleration();

// 环境检测
const isDev = process.env.NODE_ENV === 'development' || !app.isPackaged;
const VITE_DEV_SERVER_URL = process.env.VITE_DEV_SERVER_URL || 'http://localhost:3000';

let mainWindow: BrowserWindow | null = null;

/**
 * 创建主窗口
 * 需求: 1.1, 1.3, 2.1, 2.4, 3.3, 3.4
 */
function createWindow(): BrowserWindow {
  // 创建浏览器窗口
  const window = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    webPreferences: {
      // 安全配置：禁用 nodeIntegration，启用 contextIsolation
      nodeIntegration: false,
      contextIsolation: true,
      // 预加载脚本路径（将在后续任务中创建）
      preload: path.join(__dirname, 'preload.js'),
      // 允许WebSocket连接 - 在开发环境中禁用 webSecurity 以允许 WebSocket
      webSecurity: !isDev,
    },
  });

  // 加载内容
  loadContent(window);

  // 开发模式下自动打开 DevTools
  // 需求: 2.5, 4.4
  if (isDev) {
    window.webContents.openDevTools();
  }

  return window;
}

/**
 * 根据环境加载内容
 * 需求: 1.4, 1.5
 */
function loadContent(window: BrowserWindow): void {
  if (isDev) {
    // 开发环境：从 Vite 开发服务器加载
    window.loadURL(VITE_DEV_SERVER_URL);
    
    // 监听加载失败
    window.webContents.on('did-fail-load', (event, errorCode, errorDescription) => {
      console.error('Failed to load from Vite dev server:', errorDescription);
      console.error('Make sure Vite dev server is running on', VITE_DEV_SERVER_URL);
    });
  } else {
    // 生产环境：从打包的本地文件加载
    const indexPath = path.join(__dirname, '../dist/index.html');
    console.log('[Main] Loading index.html from:', indexPath);
    window.loadFile(indexPath).catch(err => {
      console.error('[Main] Failed to load index.html:', err);
    });
    
    // 监听加载错误
    window.webContents.on('did-fail-load', (event, errorCode, errorDescription) => {
      console.error('[Main] Failed to load:', errorCode, errorDescription);
    });
  }
}

/**
 * Backend API base URL
 */
const BACKEND_URL = 'http://localhost:8000';

/**
 * 通用 API 调用函数（包含超时和重试）
 * 需求: 8.3, 8.4, 8.5
 */
async function callBackendAPI(
  method: 'GET' | 'POST' | 'PATCH' | 'DELETE',
  endpoint: string,
  data?: any,
  maxRetries: number = 3
): Promise<IPCResponse> {
  let lastError: Error | null = null;

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      console.log(`[API] ${method} ${endpoint} (attempt ${attempt + 1}/${maxRetries})`);
      
      const response = await axios({
        method,
        url: `${BACKEND_URL}${endpoint}`,
        data,
        timeout: 5000, // 5 second timeout (需求: 8.5)
        headers: {
          'Content-Type': 'application/json',
        },
      });

      console.log(`[API] Success: ${method} ${endpoint}`);
      return { success: true, data: response.data };
    } catch (error) {
      lastError = error as Error;
      
      if (axios.isAxiosError(error)) {
        const axiosError = error as AxiosError;
        
        // Handle timeout
        if (axiosError.code === 'ECONNABORTED') {
          console.error(`[API] Timeout on attempt ${attempt + 1}: ${endpoint}`);
        }
        // Handle HTTP errors
        else if (axiosError.response) {
          console.error(`[API] HTTP ${axiosError.response.status}: ${endpoint}`);
          // Don't retry on client errors (4xx)
          if (axiosError.response.status >= 400 && axiosError.response.status < 500) {
            return {
              success: false,
              error: (axiosError.response.data as any)?.detail || axiosError.message,
            };
          }
        }
        // Handle network errors
        else if (axiosError.request) {
          console.error(`[API] Network error on attempt ${attempt + 1}: ${endpoint}`);
        }
      }

      // Wait before retry (exponential backoff)
      if (attempt < maxRetries - 1) {
        const delay = 1000 * (attempt + 1);
        console.log(`[API] Retrying in ${delay}ms...`);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }

  // All retries failed
  console.error(`[API] All ${maxRetries} attempts failed for ${endpoint}`);
  return {
    success: false,
    error: lastError?.message || 'Request failed after multiple retries',
  };
}

/**
 * 设置 IPC 处理器
 * 需求: 7.2, 7.4, 8.1
 */
function setupIPC(): void {
  // Ping-pong 示例通信
  // 需求: 7.4
  ipcMain.handle('ping', async () => {
    console.log('[IPC] Received ping request');
    return 'pong';
  });

  // Camera API handlers
  // 需求: 8.1

  /**
   * Get all cameras
   * 需求: 8.1
   */
  ipcMain.handle('camera:getAll', async () => {
    console.log('[IPC] camera:getAll');
    return await callBackendAPI('GET', '/api/cameras/');
  });

  /**
   * Get camera by ID
   * 需求: 8.1
   */
  ipcMain.handle('camera:getById', async (event, cameraId: string) => {
    console.log('[IPC] camera:getById', cameraId);
    return await callBackendAPI('GET', `/api/cameras/${cameraId}/`);
  });

  /**
   * Get cameras by direction
   * 需求: 8.1
   */
  ipcMain.handle('camera:getByDirection', async (event, direction: string) => {
    console.log('[IPC] camera:getByDirection', direction);
    return await callBackendAPI('GET', `/api/cameras/direction/${direction}/`);
  });

  /**
   * Create new camera
   * 需求: 8.1
   */
  ipcMain.handle('camera:create', async (event, cameraData: any) => {
    console.log('[IPC] camera:create', cameraData);
    return await callBackendAPI('POST', '/api/cameras/', cameraData);
  });

  /**
   * Update camera
   * 需求: 8.1
   */
  ipcMain.handle('camera:update', async (event, cameraId: string, updates: any) => {
    console.log('[IPC] camera:update', cameraId, updates);
    return await callBackendAPI('PATCH', `/api/cameras/${cameraId}/`, updates);
  });

  /**
   * Delete camera
   * 需求: 8.1
   */
  ipcMain.handle('camera:delete', async (event, cameraId: string) => {
    console.log('[IPC] camera:delete', cameraId);
    return await callBackendAPI('DELETE', `/api/cameras/${cameraId}/`);
  });

  /**
   * Update camera status
   * 需求: 8.1
   */
  ipcMain.handle('camera:updateStatus', async (event, cameraId: string, status: string) => {
    console.log('[IPC] camera:updateStatus', cameraId, status);
    return await callBackendAPI('PATCH', `/api/cameras/${cameraId}/status/`, { status });
  });

  // Legacy handlers (kept for backward compatibility)
  
  // 通用消息处理器
  // 需求: 7.2
  ipcMain.on('message', (event, channel: string, data: any) => {
    console.log(`[IPC] Received message on channel: ${channel}`, data);
    
    try {
      // 消息验证
      if (!channel || typeof channel !== 'string') {
        throw new Error('Invalid channel name');
      }

      // 这里可以根据不同的 channel 处理不同的消息
      // 目前只是记录日志
      const response: IPCResponse = {
        success: true,
        data: { received: true, channel, timestamp: Date.now() }
      };

      // 发送响应回渲染进程
      event.reply(`${channel}-response`, response);
    } catch (error) {
      console.error('[IPC] Error handling message:', error);
      const errorResponse: IPCResponse = {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
      event.reply(`${channel}-response`, errorResponse);
    }
  });

  // 通用请求-响应处理器
  // 需求: 7.2, 7.4
  ipcMain.handle('request', async (event, channel: string, data: any) => {
    console.log(`[IPC] Received request on channel: ${channel}`, data);
    
    try {
      // 消息验证
      if (!channel || typeof channel !== 'string') {
        throw new Error('Invalid channel name');
      }

      // 这里可以根据不同的 channel 处理不同的请求
      // 目前返回一个通用响应
      const response: IPCResponse = {
        success: true,
        data: { 
          received: true, 
          channel, 
          originalData: data,
          timestamp: Date.now() 
        }
      };

      return response;
    } catch (error) {
      console.error('[IPC] Error handling request:', error);
      const errorResponse: IPCResponse = {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
      return errorResponse;
    }
  });

  console.log('[IPC] IPC handlers initialized');
}

/**
 * 应用生命周期事件处理
 */

// 当 Electron 完成初始化时创建窗口
// 需求: 1.1, 2.1
app.whenReady().then(() => {
  // 设置 IPC 处理器
  setupIPC();
  
  // 配置session以允许WebSocket连接
  const { session } = require('electron');
  session.defaultSession.webRequest.onHeadersReceived((details: any, callback: any) => {
    callback({
      responseHeaders: {
        ...details.responseHeaders,
        'Content-Security-Policy': [
          "default-src 'self' 'unsafe-inline' 'unsafe-eval' data: blob:; " +
          "connect-src 'self' ws://localhost:* http://localhost:* ws://127.0.0.1:* http://127.0.0.1:* ws://0.0.0.0:* http://0.0.0.0:*; " +
          "img-src 'self' data: blob: https:; " +
          "style-src 'self' 'unsafe-inline'; " +
          "script-src 'self' 'unsafe-inline' 'unsafe-eval';"
        ]
      }
    });
  });
  
  mainWindow = createWindow();

  // macOS 特定行为：当应用激活且无窗口时创建新窗口
  // 需求: 2.3
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      mainWindow = createWindow();
    }
  });
});

// 当所有窗口关闭时退出应用（macOS 除外）
// 需求: 1.2, 2.2
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// 清理窗口引用
app.on('before-quit', () => {
  mainWindow = null;
});
