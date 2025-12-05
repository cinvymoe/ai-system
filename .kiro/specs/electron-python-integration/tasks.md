# 实施计划

- [x] 1. 配置 Electron 项目依赖和基础结构
  - 安装 Electron 和相关开发依赖（electron, electron-builder, concurrently, wait-on, cross-env）
  - 创建 electron 目录用于存放主进程代码
  - 配置 TypeScript 编译选项用于 Electron 代码
  - 更新 package.json 添加 main 字段指向主进程入口
  - _需求: 1.1, 1.3, 6.5_

- [x] 2. 实现 Electron 主进程
  - 创建 electron/main.ts 主进程入口文件
  - 实现窗口创建逻辑（createWindow 函数）
  - 配置窗口安全选项（禁用 nodeIntegration，启用 contextIsolation）
  - 实现环境检测和资源加载逻辑（开发环境加载 Vite 服务器，生产环境加载本地文件）
  - 处理应用生命周期事件（ready, window-all-closed, activate）
  - 在开发模式下自动打开 DevTools
  - _需求: 1.1, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 2.4, 2.5, 4.4_

- [ ]* 2.1 编写主进程单元测试
  - 测试窗口配置选项
  - 测试环境检测逻辑
  - 测试生命周期事件处理
  - _需求: 2.1, 2.4_

- [ ]* 2.2 编写属性测试：窗口配置安全性
  - **属性 2: 窗口配置安全性**
  - **验证: 需求 3.3, 3.4**
  - 生成随机窗口配置场景
  - 验证 nodeIntegration 始终为 false
  - 验证 contextIsolation 始终为 true

- [ ]* 2.3 编写属性测试：环境加载一致性
  - **属性 3: 环境加载一致性**
  - **验证: 需求 1.4, 1.5**
  - 测试不同环境标志下的加载行为
  - 验证开发环境从 Vite 服务器加载
  - 验证生产环境从本地文件加载

- [x] 3. 实现预加载脚本
  - 创建 electron/preload.ts 预加载脚本
  - 使用 contextBridge 暴露安全的 API 接口
  - 实现 ping 测试方法
  - 实现通用的 IPC 通信接口（send, on）
  - 暴露系统信息（platform, version）
  - 创建 TypeScript 类型定义文件（electron/types.ts）
  - _需求: 3.1, 3.2, 3.5, 7.1_

- [ ]* 3.1 编写预加载脚本测试
  - 测试 contextBridge API 暴露
  - 测试 API 接口可用性
  - _需求: 3.2_

- [x] 4. 配置主进程 IPC 处理器
  - 在主进程中设置 IPC 处理器
  - 实现 ping-pong 示例通信
  - 实现通用消息处理和错误处理
  - 添加消息验证和日志记录
  - _需求: 7.2, 7.4_

- [ ]* 4.1 编写属性测试：IPC 通信往返一致性
  - **属性 1: IPC 通信往返一致性**
  - **验证: 需求 7.2, 7.3**
  - 生成随机的有效 IPC 消息
  - 验证响应格式和数据完整性
  - 测试错误处理机制

- [x] 5. 调整 Vite 配置以支持 Electron
  - 修改 vite.config.ts 添加 Electron 环境支持
  - 设置 base 路径为相对路径（生产环境）
  - 配置构建输出目录
  - 确保开发服务器端口配置正确
  - _需求: 1.4, 1.5, 4.1_

- [x] 6. 配置开发和构建脚本
  - 在 package.json 中添加 dev 脚本（并行启动 Vite 和 Electron）
  - 添加 dev:vite 和 dev:electron 脚本
  - 添加 build 脚本（构建前端和主进程）
  - 添加 build:vite 和 build:electron 脚本
  - 配置 electron-builder 打包选项（创建 electron-builder.yml）
  - _需求: 6.1, 6.2, 6.3, 6.4_

- [x] 7. 在前端添加 IPC 通信测试界面
  - 在现有前端中添加测试组件或页面
  - 调用 window.electronAPI.ping() 测试通信
  - 显示通信测试结果（成功/失败，响应内容）
  - 添加基本的错误处理和用户反馈
  - _需求: 7.3, 7.5_

- [ ]* 7.1 编写前端集成测试
  - 测试 electronAPI 可用性
  - 测试 ping-pong 通信
  - 测试错误场景
  - _需求: 7.3, 7.5_

- [x] 8. 初始化 Python 后端项目结构
  - 创建 backend 目录
  - 使用 uv init 初始化 Python 项目
  - 配置 pyproject.toml（项目名称、版本、依赖）
  - 添加 FastAPI 和 uvicorn 作为依赖
  - 创建基本目录结构（src, tests）
  - 使用 uv venv 创建虚拟环境
  - 创建 backend/src/main.py 入口文件（包含简单的 Hello World）
  - 添加 backend/README.md 说明文档
  - _需求: 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ]* 8.1 验证 Python 项目结构
  - 检查目录结构完整性
  - 验证 pyproject.toml 格式
  - 测试虚拟环境创建
  - 测试依赖安装
  - _需求: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 9. 测试和验证完整工作流
  - 运行 dev 脚本验证开发模式
  - 验证 Electron 窗口正常显示现有前端界面
  - 测试前端 IPC 通信功能
  - 验证主进程代码更改后自动重启
  - 验证前端代码更改后 HMR 生效
  - 运行 build 脚本验证构建流程
  - 测试构建后的应用能否正常运行
  - _需求: 1.1, 1.2, 4.1, 4.2, 4.3, 6.1, 6.2_

- [ ] 10. 文档和清理
  - 更新项目 README.md 添加 Electron 开发说明
  - 添加开发环境设置指南
  - 添加构建和打包说明
  - 添加 Python 后端开发指南
  - 清理不必要的文件和依赖
  - 添加 .gitignore 条目（dist-electron, backend/.venv 等）
  - _需求: 所有_
