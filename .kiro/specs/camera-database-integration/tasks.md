# 实施计划

- [x] 1. 设置后端数据库基础设施
  - 配置 SQLAlchemy 和 SQLite 数据库连接
  - 创建数据库初始化脚本
  - 更新 pyproject.toml 添加必要依赖（sqlalchemy, pydantic）
  - _需求: 1.1, 1.4_

- [x] 2. 实现数据库模型层（Model）
  - [x] 2.1 创建 Camera SQLAlchemy ORM 模型
    - 定义所有字段（id, name, url, enabled, resolution, fps, brightness, contrast, status, direction, timestamps）
    - 添加表索引（direction, status）
    - _需求: 1.2_

  - [x] 2.2 创建 Pydantic 验证模式
    - 实现 CameraBase, CameraCreate, CameraUpdate, CameraResponse 模式
    - 添加字段验证器（URL 格式、数值范围、分辨率格式）
    - _需求: 10.1, 10.2, 10.3_

- [x] 3. 实现 Repository 层（数据访问）
  - [x] 3.1 创建 CameraRepository 类
    - 实现 get_all() 方法
    - 实现 get_by_id() 方法
    - 实现 get_by_direction() 方法
    - 实现 create() 方法
    - 实现 update() 方法
    - 实现 delete() 方法
    - 实现 exists_by_name() 方法
    - _需求: 2.1, 3.2, 4.2, 5.1_

- [x] 4. 实现 Service 层（业务逻辑）
  - [x] 4.1 创建 CameraService 类
    - 实现 get_all_cameras() 方法
    - 实现 get_camera_by_id() 方法
    - 实现 get_cameras_by_direction() 方法
    - 实现 create_camera() 方法（包含名称重复检查）
    - 实现 update_camera() 方法（包含名称重复检查）
    - 实现 delete_camera() 方法
    - 实现 update_camera_status() 方法
    - _需求: 2.1, 3.1, 3.5, 4.1, 5.1, 6.1, 9.1_

  - [x] 4.2 添加错误处理和日志记录
    - 处理数据库连接错误
    - 处理约束违反错误
    - 记录所有操作日志
    - _需求: 1.3, 3.4, 5.5_

- [x] 5. 实现 API 路由层
  - [x] 5.1 创建 cameras API 路由
    - GET /api/cameras - 获取所有摄像头
    - GET /api/cameras/{id} - 获取单个摄像头
    - GET /api/cameras/direction/{direction} - 按方向获取
    - POST /api/cameras - 创建摄像头
    - PATCH /api/cameras/{id} - 更新摄像头
    - DELETE /api/cameras/{id} - 删除摄像头
    - PATCH /api/cameras/{id}/status - 更新状态
    - _需求: 2.1, 3.2, 4.2, 5.1, 6.1, 9.1_

  - [x] 5.2 配置依赖注入
    - 实现 get_db() 依赖
    - 实现 get_camera_service() 依赖
    - _需求: 8.2_

- [x] 6. 更新 FastAPI 主应用
  - [x] 6.1 集成 cameras 路由到主应用
    - 在 main.py 中注册路由
    - 配置 CORS 中间件
    - 添加启动时数据库初始化
    - _需求: 1.1, 8.2_

- [x] 7. 实现 Electron IPC 通信层
  - [x] 7.1 更新主进程 IPC 处理器
    - 添加 camera:getAll 处理器
    - 添加 camera:getById 处理器
    - 添加 camera:getByDirection 处理器
    - 添加 camera:create 处理器
    - 添加 camera:update 处理器
    - 添加 camera:delete 处理器
    - 添加 camera:updateStatus 处理器
    - 实现通用 API 调用函数（包含超时和重试）
    - _需求: 8.1, 8.3, 8.4, 8.5_

  - [x] 7.2 更新预加载脚本
    - 通过 contextBridge 暴露 cameraAPI
    - 添加 TypeScript 类型定义
    - _需求: 8.1_

- [x] 8. 实现前端 Service 层
  - [x] 8.1 创建 CameraService 类
    - 实现 getAllCameras() 方法
    - 实现 getCameraById() 方法
    - 实现 getCamerasByDirection() 方法
    - 实现 createCamera() 方法
    - 实现 updateCamera() 方法
    - 实现 deleteCamera() 方法
    - 实现 updateCameraStatus() 方法
    - 添加错误处理
    - _需求: 8.1, 8.3_

- [x] 9. 实现 ViewModel 层（状态管理）
  - [x] 9.1 创建 Zustand camera store
    - 定义状态接口（cameras, loading, error）
    - 实现 fetchCameras action
    - 实现 fetchCamerasByDirection action
    - 实现 addCamera action
    - 实现 updateCamera action
    - 实现 deleteCamera action
    - 实现 toggleCameraEnabled action
    - 实现 updateCameraStatus action
    - 实现乐观更新和回滚逻辑
    - _需求: 2.1, 3.2, 4.2, 4.3, 4.4, 5.1, 5.2, 6.1, 6.2, 6.3, 7.5_

- [x] 10. 更新 View 层组件
  - [x] 10.1 更新 CameraListSettings 组件
    - 集成 useCameraStore hook
    - 从 store 获取摄像头数据
    - 实现加载状态显示
    - 实现错误状态显示
    - 更新删除操作调用 store action
    - 更新启用/禁用切换调用 store action
    - _需求: 2.1, 2.2, 2.3, 2.4, 4.3, 5.2, 6.2_

  - [x] 10.2 更新 AddCameraSettings 组件
    - 集成 useCameraStore hook
    - 调用 addCamera action 保存数据
    - 显示验证错误信息
    - 显示保存成功/失败提示
    - _需求: 3.1, 3.2, 3.4, 3.5_

  - [x] 10.3 更新 EditCameraSettings 组件
    - 集成 useCameraStore hook
    - 调用 updateCamera action 保存更改
    - 显示验证错误信息
    - 显示更新成功/失败提示
    - _需求: 4.1, 4.2, 4.3, 4.4, 4.5_

  - [x] 10.4 更新 App.tsx 移除本地状态
    - 移除 cameraGroups 本地状态
    - 使用 useCameraStore 替代
    - 更新所有摄像头相关操作
    - _需求: 7.5_

- [x] 11. 数据迁移和初始化
  - [x] 11.1 创建数据迁移脚本
    - 从 App.tsx 的初始数据迁移到数据库
    - 提供数据导入/导出功能
    - _需求: 1.5_

- [x] 12. 手动测试和验证
  - 按照设计文档中的手动测试清单进行测试
  - 验证所有 CRUD 操作
  - 验证数据持久化
  - 验证错误处理
  - 验证 UI 交互
  - 记录测试结果和问题
  - _需求: 所有需求_

- [ ] 13. 最终检查点
  - 确保所有功能正常工作
  - 确保数据在重启后保持
  - 确保错误提示清晰友好
  - 询问用户是否有问题或需要调整
