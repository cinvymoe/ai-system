# 设计文档

## 概述

本设计文档描述了如何将现有的 Vite + React + TypeScript 前端应用转换为 Electron 桌面应用，并搭建使用 uv 管理的 Python 后端项目结构。设计重点在于建立基础框架，而非实现具体业务功能。

### 设计目标

1. 保持现有前端代码不变，仅添加 Electron 包装层
2. 配置安全的 Electron 环境（禁用 nodeIntegration，启用 contextIsolation）
3. 建立高效的开发工作流（HMR、自动重启）
4. 使用 uv 搭建现代化的 Python 项目结构
5. 实现基本的前后端通信机制验证

## 架构

### 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                    Electron 应用                         │
│  ┌──────────────────┐         ┌────────────────────┐   │
│  │   主进程 (Main)   │◄───IPC──►│ 渲染进程 (Renderer)│   │
│  │   - 窗口管理      │         │   - React 前端     │   │
│  │   - 生命周期      │         │   - Vite HMR       │   │
│  │   - IPC 处理      │         │                    │   │
│  └──────────────────┘         └────────────────────┘   │
│           │                              ▲              │
│           │                              │              │
│           │                    ┌─────────┴────────┐    │
│           │                    │   预加载脚本      │    │
│           │                    │  - contextBridge  │    │
│           │                    │  - IPC API 暴露   │    │
│           │                    └──────────────────┘    │
└───────────┼──────────────────────────────────────────┘
            │
            │ (未来扩展)
            ▼
   ┌────────────────┐
   │  Python 后端    │
   │  - uv 管理      │
   │  - FastAPI/Flask│
   └────────────────┘
```

### 目录结构

```
project-root/
├── electron/                 # Electron 主进程代码
│   ├── main.ts              # 主进程入口
│   ├── preload.ts           # 预加载脚本
│   └── types.ts             # TypeScript 类型定义
├── backend/                 # Python 后端
│   ├── src/                 # 源代码
│   │   └── main.py         # 后端入口
│   ├── tests/              # 测试
│   ├── pyproject.toml      # uv 项目配置
│   └── .venv/              # 虚拟环境（由 uv 创建）
├── src/                    # 现有前端代码（保持不变）
│   ├── components/
│   ├── App.tsx
│   └── main.tsx
├── dist-electron/          # Electron 构建输出
├── dist/                   # 前端构建输出
├── package.json            # Node.js 依赖和脚本
├── electron-builder.yml    # Electron 打包配置
├── vite.config.ts          # Vite 配置（需要调整）
└── tsconfig.json           # TypeScript 配置
```

## 组件和接口

### 1. Electron 主进程 (electron/main.ts)

**职责：**
- 创建和管理应用窗口
- 处理应用生命周期事件
- 接收和处理来自渲染进程的 IPC 消息
- 根据环境（开发/生产）加载不同的资源

**关键接口：**

```typescript
// 窗口配置
interface WindowConfig {
  width: number;
  height: number;
  webPreferences: {
    preload: string;
    nodeIntegration: boolean;
    contextIsolation: boolean;
  };
}

// 应用配置
interface AppConfig {
  isDev: boolean;
  viteDevServerUrl?: string;
  indexHtmlPath?: string;
}
```

**核心功能：**
- `createWindow()`: 创建主窗口
- `loadContent()`: 根据环境加载内容
- `setupIPC()`: 设置 IPC 处理器
- `handleAppEvents()`: 处理应用生命周期事件

### 2. 预加载脚本 (electron/preload.ts)

**职责：**
- 在渲染进程加载前执行
- 通过 contextBridge 安全地暴露 API 给渲染进程
- 作为主进程和渲染进程之间的桥梁

**暴露的 API：**

```typescript
// 暴露给渲染进程的 API
interface ElectronAPI {
  // 基础通信
  ping: () => Promise<string>;
  
  // IPC 通信
  send: (channel: string, data: any) => void;
  on: (channel: string, callback: Function) => void;
  
  // 系统信息
  platform: string;
  version: string;
}

// 在 window 对象上的类型
declare global {
  interface Window {
    electronAPI: ElectronAPI;
  }
}
```

### 3. IPC 通信机制

**通信模式：**

1. **单向通信（渲染 → 主）：**
   ```typescript
   // 渲染进程
   window.electronAPI.send('channel-name', data);
   
   // 主进程
   ipcMain.on('channel-name', (event, data) => {
     // 处理消息
   });
   ```

2. **请求-响应模式：**
   ```typescript
   // 渲染进程
   const result = await window.electronAPI.ping();
   
   // 主进程
   ipcMain.handle('ping', async () => {
     return 'pong';
   });
   ```

### 4. Python 后端结构

**项目结构：**

```
backend/
├── src/
│   ├── __init__.py
│   ├── main.py           # 应用入口
│   ├── api/              # API 路由（未来）
│   ├── core/             # 核心业务逻辑（未来）
│   └── models/           # 数据模型（未来）
├── tests/
│   └── __init__.py
├── pyproject.toml        # 项目配置
└── README.md
```

**pyproject.toml 配置：**

```toml
[project]
name = "vision-security-backend"
version = "0.1.0"
description = "Python backend for vision security monitoring system"
requires-python = ">=3.10"
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn>=0.24.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

## 数据模型

### IPC 消息格式

```typescript
// 通用消息格式
interface IPCMessage<T = any> {
  channel: string;
  data: T;
  timestamp: number;
}

// 响应格式
interface IPCResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
}
```

### 配置数据

```typescript
// 应用配置
interface AppSettings {
  window: {
    width: number;
    height: number;
    minWidth: number;
    minHeight: number;
  };
  dev: {
    openDevTools: boolean;
    vitePort: number;
  };
}
```

## 正确性属性

*属性是指在系统的所有有效执行中都应该成立的特征或行为——本质上是关于系统应该做什么的形式化陈述。属性作为人类可读规范和机器可验证正确性保证之间的桥梁。*

### 属性反思

在分析所有验收标准后，我们发现大多数标准都是针对特定配置和环境的示例测试，而不是通用属性。这些测试主要验证：
- 配置文件的正确性（package.json、pyproject.toml）
- 开发工具的集成（Vite HMR、DevTools）
- 项目结构的完整性（目录、文件存在）

由于这是框架搭建阶段，重点在于配置和集成，因此大部分验收标准更适合通过示例测试和集成测试来验证，而不是属性测试。

以下是识别出的可以用属性测试的场景：

### 属性 1：IPC 通信往返一致性

*对于任何* 有效的 IPC 消息，当渲染进程发送消息到主进程并接收响应时，响应应该包含预期的数据结构和成功状态。

**验证：需求 7.2, 7.3**

### 属性 2：窗口配置安全性

*对于任何* 创建的 BrowserWindow 实例，nodeIntegration 应该始终为 false，contextIsolation 应该始终为 true。

**验证：需求 3.3, 3.4**

### 属性 3：环境加载一致性

*对于任何* 给定的环境标志（开发/生产），应用应该始终从正确的源加载内容（开发环境从 Vite 服务器，生产环境从本地文件）。

**验证：需求 1.4, 1.5**

## 错误处理

### 1. 窗口创建失败

```typescript
try {
  mainWindow = createWindow();
} catch (error) {
  console.error('Failed to create window:', error);
  app.quit();
}
```

### 2. 资源加载失败

```typescript
mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription) => {
  console.error('Failed to load:', errorDescription);
  // 显示错误页面或重试
});
```

### 3. IPC 通信错误

```typescript
ipcMain.handle('some-channel', async (event, data) => {
  try {
    const result = await processData(data);
    return { success: true, data: result };
  } catch (error) {
    return { success: false, error: error.message };
  }
});
```

### 4. Python 环境错误

- uv 未安装：提示用户安装 uv
- 虚拟环境创建失败：检查权限和磁盘空间
- 依赖安装失败：检查网络连接和包名称

## 测试策略

### 单元测试

**主进程测试：**
- 窗口配置验证
- IPC 处理器逻辑
- 环境检测逻辑

**预加载脚本测试：**
- API 暴露验证
- contextBridge 配置

**工具：**
- Jest 或 Vitest
- @electron/test-utils（可选）

### 属性测试

**测试库：** fast-check (JavaScript/TypeScript 的属性测试库)

**配置：** 每个属性测试应运行至少 100 次迭代

**测试标记格式：** `// Feature: electron-python-integration, Property {number}: {property_text}`

**属性测试用例：**

1. **IPC 通信往返一致性测试**
   - 生成随机的有效 IPC 消息
   - 验证响应格式和数据完整性
   - 标记：`// Feature: electron-python-integration, Property 1: IPC 通信往返一致性`

2. **窗口配置安全性测试**
   - 验证所有窗口实例的安全配置
   - 标记：`// Feature: electron-python-integration, Property 2: 窗口配置安全性`

3. **环境加载一致性测试**
   - 测试不同环境标志下的加载行为
   - 标记：`// Feature: electron-python-integration, Property 3: 环境加载一致性`

### 集成测试

**测试场景：**
- 完整的应用启动和关闭流程
- 前端界面加载和显示
- IPC 通信端到端测试
- Python 项目结构验证

**工具：**
- Spectron（已废弃，考虑使用 Playwright for Electron）
- 手动测试清单

### 测试优先级

1. **高优先级：** 安全配置测试（nodeIntegration、contextIsolation）
2. **中优先级：** IPC 通信测试、窗口创建测试
3. **低优先级：** 开发工具集成测试、构建输出验证

## 开发工作流

### 开发模式

1. 启动 Vite 开发服务器（端口 3000）
2. 启动 Electron 应用，连接到 Vite 服务器
3. 前端代码更改 → Vite HMR 自动更新
4. 主进程代码更改 → 自动重启 Electron

**实现方式：**
- 使用 `electron-vite` 或 `concurrently` 同时运行多个进程
- 使用 `nodemon` 或 `electron-reload` 监听主进程文件变化

### 构建流程

1. 构建前端：`vite build`
2. 构建主进程：`tsc` 编译 TypeScript
3. 打包应用：`electron-builder`

### Python 开发流程

1. 初始化项目：`uv init`
2. 创建虚拟环境：`uv venv`
3. 安装依赖：`uv pip install -r pyproject.toml`
4. 运行后端：`uv run python src/main.py`

## 技术选型

### Electron 相关

- **Electron**: ^28.0.0（最新稳定版）
- **electron-builder**: 打包工具
- **electron-vite**: 构建工具（可选，或使用 vite + concurrently）

### 开发工具

- **TypeScript**: 类型安全
- **concurrently**: 并行运行多个命令
- **wait-on**: 等待服务就绪
- **cross-env**: 跨平台环境变量

### Python 工具

- **uv**: 包管理和虚拟环境
- **FastAPI**: Web 框架（未来使用）
- **uvicorn**: ASGI 服务器（未来使用）

## 配置文件

### package.json 脚本

```json
{
  "scripts": {
    "dev": "concurrently \"npm run dev:vite\" \"npm run dev:electron\"",
    "dev:vite": "vite",
    "dev:electron": "wait-on http://localhost:3000 && electron .",
    "build": "npm run build:vite && npm run build:electron",
    "build:vite": "vite build",
    "build:electron": "tsc -p electron/tsconfig.json",
    "pack": "electron-builder --dir",
    "dist": "electron-builder"
  }
}
```

### Vite 配置调整

```typescript
export default defineConfig({
  // ... 现有配置
  base: process.env.ELECTRON === 'true' ? './' : '/',
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
});
```

### electron-builder 配置

```yaml
appId: com.vision.security
productName: Vision Security Monitor
directories:
  output: release
  buildResources: build
files:
  - dist/**/*
  - dist-electron/**/*
  - package.json
extraResources:
  - backend/**/*
  - "!backend/.venv"
  - "!backend/**/__pycache__"
```

## 安全考虑

### 1. 渲染进程隔离

- 禁用 `nodeIntegration`
- 启用 `contextIsolation`
- 使用 `contextBridge` 暴露 API

### 2. 内容安全策略

```typescript
session.defaultSession.webRequest.onHeadersReceived((details, callback) => {
  callback({
    responseHeaders: {
      ...details.responseHeaders,
      'Content-Security-Policy': ["default-src 'self'"]
    }
  });
});
```

### 3. IPC 消息验证

- 验证消息来源
- 验证消息格式
- 限制可调用的 API

## 性能考虑

### 1. 启动优化

- 延迟加载非关键模块
- 使用 `ready-to-show` 事件显示窗口
- 预加载关键资源

### 2. 内存管理

- 及时清理不用的窗口
- 限制 IPC 消息大小
- 使用流处理大数据

### 3. 构建优化

- 代码分割
- Tree shaking
- 压缩资源文件

## 未来扩展

### 1. Python 后端集成

- 主进程启动 Python 子进程
- HTTP 或 WebSocket 通信
- 进程监控和自动重启

### 2. 自动更新

- 使用 `electron-updater`
- 配置更新服务器
- 实现增量更新

### 3. 原生功能

- 系统托盘
- 全局快捷键
- 通知
- 文件系统访问

## 部署考虑

### 1. 打包策略

- 为不同平台构建不同的安装包
- 包含 Python 运行时（未来）
- 代码签名（生产环境）

### 2. 分发方式

- 直接下载安装包
- 自动更新服务
- 应用商店（可选）

### 3. 版本管理

- 语义化版本号
- 变更日志
- 回滚机制
