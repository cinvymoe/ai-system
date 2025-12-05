# 需求文档

## 简介

为现有的基于 Vite + React + TypeScript 的视觉安全监控系统前端应用搭建 Electron 桌面应用框架，并建立 Python 后端项目结构（使用 uv 管理）。本阶段仅搭建基础框架，不实现具体业务功能。

## 术语表

- **Electron应用**: 使用 Electron 框架构建的跨平台桌面应用程序
- **主进程**: Electron 应用中运行 Node.js 的主要进程，负责创建窗口和管理应用生命周期
- **渲染进程**: Electron 应用中运行前端代码（React）的进程
- **Python后端**: 使用 Python 编写的后端服务框架
- **uv**: Python 的现代包管理工具，用于管理依赖和虚拟环境
- **预加载脚本**: Electron 中在渲染进程加载前执行的脚本，用于安全地暴露 API

## 需求

### 需求 1

**用户故事:** 作为开发者，我希望搭建 Electron 应用基础框架，以便现有的 React 前端可以在 Electron 环境中运行。

#### 验收标准

1. WHEN 开发者运行开发命令 THEN Electron应用 SHALL 启动并显示现有的 React 界面
2. WHEN 用户关闭应用窗口 THEN Electron应用 SHALL 完全退出
3. WHEN Electron应用启动 THEN 主进程 SHALL 创建应用窗口并加载渲染进程
4. WHERE 在开发环境 THEN Electron应用 SHALL 从 Vite 开发服务器加载前端
5. WHERE 在生产环境 THEN Electron应用 SHALL 从打包的资源加载前端代码

### 需求 2

**用户故事:** 作为开发者，我希望配置 Electron 主进程，以便管理应用窗口和生命周期。

#### 验收标准

1. WHEN 主进程 启动 THEN 主进程 SHALL 创建一个浏览器窗口实例
2. WHEN 所有窗口关闭 THEN 主进程 SHALL 退出应用（macOS 除外）
3. WHEN 应用激活且无窗口 THEN 主进程 SHALL 创建新窗口
4. WHEN 窗口创建 THEN 主进程 SHALL 配置窗口大小和安全选项
5. WHERE 在开发模式 THEN 主进程 SHALL 自动打开开发者工具

### 需求 3

**用户故事:** 作为开发者，我希望配置预加载脚本，以便安全地在渲染进程中暴露必要的 API。

#### 验收标准

1. WHEN 渲染进程 加载 THEN 预加载脚本 SHALL 在页面加载前执行
2. WHEN 预加载脚本 执行 THEN 预加载脚本 SHALL 通过 contextBridge 暴露 API
3. WHEN 配置窗口 THEN 主进程 SHALL 禁用 nodeIntegration
4. WHEN 配置窗口 THEN 主进程 SHALL 启用 contextIsolation
5. WHERE 暴露 API THEN 预加载脚本 SHALL 仅暴露必要的安全接口

### 需求 4

**用户故事:** 作为开发者，我希望配置 Electron 开发环境，以便高效开发和调试。

#### 验收标准

1. WHEN 开发者启动开发模式 THEN Electron应用 SHALL 连接到 Vite 开发服务器
2. WHEN 前端代码更改 THEN 渲染进程 SHALL 通过 Vite HMR 自动更新
3. WHEN 主进程代码更改 THEN 开发工具 SHALL 重启 Electron 应用
4. WHEN 开发模式运行 THEN Electron应用 SHALL 自动打开 Chrome DevTools
5. WHERE 使用 electron-vite THEN 构建工具 SHALL 同时处理主进程和渲染进程

### 需求 5

**用户故事:** 作为开发者，我希望使用 uv 搭建 Python 后端项目结构，以便管理 Python 依赖和环境。

#### 验收标准

1. WHEN 创建 Python后端 项目 THEN 项目结构 SHALL 包含独立的 backend 目录
2. WHEN 初始化 Python 项目 THEN uv SHALL 创建 pyproject.toml 配置文件
3. WHEN 定义项目依赖 THEN pyproject.toml SHALL 列出所有 Python 包依赖
4. WHEN 创建虚拟环境 THEN uv SHALL 在项目中创建 .venv 目录
5. WHERE 组织代码 THEN Python后端 SHALL 包含基本的目录结构（如 src、tests）

### 需求 6

**用户故事:** 作为开发者，我希望配置项目构建脚本，以便统一管理开发和构建流程。

#### 验收标准

1. WHEN 开发者运行 dev 命令 THEN 构建脚本 SHALL 同时启动 Vite 和 Electron
2. WHEN 开发者运行 build 命令 THEN 构建脚本 SHALL 构建前端和主进程代码
3. WHEN 配置 package.json THEN 项目 SHALL 包含 dev、build、start 等脚本
4. WHERE 使用 electron-builder THEN 配置文件 SHALL 定义打包选项
5. WHERE 管理依赖 THEN package.json SHALL 包含所有必要的 Electron 和构建工具依赖

### 需求 7

**用户故事:** 作为开发者，我希望建立基本的前后端通信机制，以便验证框架搭建成功。

#### 验收标准

1. WHEN 前端发送测试请求 THEN 预加载脚本 SHALL 提供简单的 IPC 通信接口
2. WHEN 主进程 接收 IPC 消息 THEN 主进程 SHALL 返回响应给渲染进程
3. WHEN 测试通信 THEN 前端 SHALL 能够调用预加载脚本暴露的 API
4. WHERE 实现示例 THEN 系统 SHALL 包含一个简单的 ping-pong 通信示例
5. WHERE 验证功能 THEN 前端界面 SHALL 显示通信测试结果
