import { useState } from 'react';
import { Zap, CheckCircle, XCircle, Info } from 'lucide-react';

/**
 * Electron IPC 通信测试组件
 * 需求: 7.3, 7.5
 * 
 * 功能:
 * - 测试 window.electronAPI.ping() 通信
 * - 显示通信测试结果（成功/失败，响应内容）
 * - 提供基本的错误处理和用户反馈
 */

// 引入 Electron API 类型定义
/// <reference path="../../electron/types.ts" />
export function ElectronIPCTest() {
  const [testResult, setTestResult] = useState<{
    status: 'idle' | 'testing' | 'success' | 'error';
    message: string;
    response?: string;
    timestamp?: Date;
  }>({
    status: 'idle',
    message: '点击按钮测试 Electron IPC 通信'
  });

  const [systemInfo, setSystemInfo] = useState<{
    platform?: string;
    version?: string;
    available: boolean;
  }>({
    available: false
  });

  // 检查 Electron API 是否可用
  const checkElectronAPI = () => {
    if (typeof window !== 'undefined' && window.electronAPI) {
      setSystemInfo({
        platform: window.electronAPI.platform,
        version: window.electronAPI.version,
        available: true
      });
      return true;
    }
    return false;
  };

  // 测试 ping 通信
  const handlePingTest = async () => {
    setTestResult({
      status: 'testing',
      message: '正在测试通信...'
    });

    try {
      // 检查 API 是否可用
      if (!checkElectronAPI()) {
        setTestResult({
          status: 'error',
          message: 'Electron API 不可用。请在 Electron 环境中运行此应用。',
          timestamp: new Date()
        });
        return;
      }

      // 调用 ping 方法
      const response = await window.electronAPI.ping();
      
      // 验证响应
      if (response === 'pong') {
        setTestResult({
          status: 'success',
          message: 'IPC 通信测试成功！',
          response: response,
          timestamp: new Date()
        });
      } else {
        setTestResult({
          status: 'error',
          message: `意外的响应: ${response}`,
          response: response,
          timestamp: new Date()
        });
      }
    } catch (error) {
      // 错误处理
      const errorMessage = error instanceof Error ? error.message : '未知错误';
      setTestResult({
        status: 'error',
        message: `通信失败: ${errorMessage}`,
        timestamp: new Date()
      });
    }
  };

  // 获取状态图标
  const getStatusIcon = () => {
    switch (testResult.status) {
      case 'success':
        return <CheckCircle className="size-6 text-green-400" />;
      case 'error':
        return <XCircle className="size-6 text-red-400" />;
      case 'testing':
        return <Zap className="size-6 text-yellow-400 animate-pulse" />;
      default:
        return <Info className="size-6 text-cyan-400" />;
    }
  };

  // 获取状态颜色类
  const getStatusColorClass = () => {
    switch (testResult.status) {
      case 'success':
        return 'border-green-500/50 bg-green-500/10';
      case 'error':
        return 'border-red-500/50 bg-red-500/10';
      case 'testing':
        return 'border-yellow-500/50 bg-yellow-500/10';
      default:
        return 'border-cyan-500/50 bg-cyan-500/10';
    }
  };

  return (
    <div className="p-6 space-y-4">
      <div className="bg-slate-800/50 rounded-lg border border-slate-700/50 p-6 space-y-4">
        <h3 className="text-lg font-semibold text-slate-100 flex items-center gap-2">
          <Zap className="size-5 text-cyan-400" />
          Electron IPC 通信测试
        </h3>

        {/* 测试按钮 */}
        <button
          onClick={handlePingTest}
          disabled={testResult.status === 'testing'}
          className="w-full px-4 py-3 bg-cyan-600 hover:bg-cyan-500 disabled:bg-slate-600 disabled:cursor-not-allowed text-white rounded-lg transition-colors duration-200 font-medium"
        >
          {testResult.status === 'testing' ? '测试中...' : '测试 Ping 通信'}
        </button>

        {/* 测试结果显示 */}
        <div className={`rounded-lg border p-4 transition-all duration-300 ${getStatusColorClass()}`}>
          <div className="flex items-start gap-3">
            <div className="mt-0.5">{getStatusIcon()}</div>
            <div className="flex-1 space-y-2">
              <p className="text-slate-100 font-medium">{testResult.message}</p>
              
              {testResult.response && (
                <div className="bg-slate-900/50 rounded p-2 border border-slate-700/50">
                  <p className="text-sm text-slate-300">
                    <span className="text-cyan-400 font-mono">响应:</span> {testResult.response}
                  </p>
                </div>
              )}
              
              {testResult.timestamp && (
                <p className="text-xs text-slate-400">
                  测试时间: {testResult.timestamp.toLocaleTimeString('zh-CN')}
                </p>
              )}
            </div>
          </div>
        </div>

        {/* 系统信息 */}
        {systemInfo.available && (
          <div className="bg-slate-900/50 rounded-lg border border-slate-700/50 p-4 space-y-2">
            <h4 className="text-sm font-semibold text-slate-300 mb-2">系统信息</h4>
            <div className="space-y-1 text-sm">
              <p className="text-slate-400">
                <span className="text-cyan-400 font-mono">平台:</span> {systemInfo.platform}
              </p>
              <p className="text-slate-400">
                <span className="text-cyan-400 font-mono">Electron 版本:</span> {systemInfo.version}
              </p>
            </div>
          </div>
        )}

        {/* 说明文本 */}
        <div className="text-xs text-slate-500 space-y-1">
          <p>• 此测试验证 Electron 主进程与渲染进程之间的 IPC 通信</p>
          <p>• 成功的测试应该返回 "pong" 响应</p>
          <p>• 如果在浏览器中运行，API 将不可用</p>
        </div>
      </div>
    </div>
  );
}
