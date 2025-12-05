# 需求文档

## 简介

为视觉安全监控系统的摄像头列表界面添加 Python 后端数据库交互功能，采用 MVVM（Model-View-ViewModel）架构模式。实现摄像头数据的持久化存储、查询、更新和删除操作，确保前后端数据同步和一致性。

## 术语表

- **MVVM**: Model-View-ViewModel 架构模式，用于分离用户界面逻辑和业务逻辑
- **Model**: 数据模型层，负责数据的存储和业务逻辑
- **View**: 视图层，即 React 组件，负责 UI 展示
- **ViewModel**: 视图模型层，连接 View 和 Model，处理数据转换和状态管理
- **数据库**: 用于持久化存储摄像头配置和状态信息的存储系统
- **IPC通信**: Electron 进程间通信机制，用于前端与后端的数据交互
- **摄像头实体**: 包含摄像头配置信息的数据对象
- **同步机制**: 确保前端显示数据与后端数据库数据一致的机制

## 需求

### 需求 1

**用户故事:** 作为开发者，我希望在 Python 后端建立数据库模型，以便持久化存储摄像头配置信息。

#### 验收标准

1. WHEN Python后端 启动 THEN 数据库 SHALL 自动初始化并创建必要的表结构
2. WHEN 定义摄像头模型 THEN Model SHALL 包含所有必要的字段（id、name、url、status、enabled、resolution、fps、brightness、contrast、direction）
3. WHEN 数据库操作失败 THEN 系统 SHALL 记录错误日志并返回明确的错误信息
4. WHERE 使用 SQLite THEN 数据库文件 SHALL 存储在应用数据目录中
5. WHEN 应用首次启动 THEN 数据库 SHALL 创建默认的表结构而不丢失现有数据

### 需求 2

**用户故事:** 作为用户，我希望摄像头列表从数据库加载，以便在应用重启后保留配置。

#### 验收标准

1. WHEN 用户打开摄像头列表界面 THEN 系统 SHALL 从数据库加载所有摄像头数据
2. WHEN 数据库为空 THEN 界面 SHALL 显示空状态提示
3. WHEN 数据加载失败 THEN 界面 SHALL 显示错误提示并提供重试选项
4. WHEN 数据加载成功 THEN 界面 SHALL 按方向分组显示摄像头
5. WHEN 加载大量摄像头数据 THEN 系统 SHALL 在 2 秒内完成加载并显示

### 需求 3

**用户故事:** 作为用户，我希望添加新摄像头时数据保存到数据库，以便配置持久化。

#### 验收标准

1. WHEN 用户提交新摄像头配置 THEN 系统 SHALL 验证数据完整性
2. WHEN 数据验证通过 THEN 系统 SHALL 将摄像头信息保存到数据库
3. WHEN 保存成功 THEN 系统 SHALL 返回新创建的摄像头 ID
4. WHEN 保存失败 THEN 系统 SHALL 返回具体的错误原因
5. WHEN 摄像头名称重复 THEN 系统 SHALL 拒绝保存并提示用户

### 需求 4

**用户故事:** 作为用户，我希望修改摄像头配置时更新数据库，以便更改持久化。

#### 验收标准

1. WHEN 用户修改摄像头配置 THEN 系统 SHALL 验证修改后的数据
2. WHEN 验证通过 THEN 系统 SHALL 更新数据库中对应的记录
3. WHEN 更新成功 THEN 界面 SHALL 立即反映最新数据
4. WHEN 更新失败 THEN 系统 SHALL 保持原有数据不变
5. WHEN 摄像头不存在 THEN 系统 SHALL 返回"未找到"错误

### 需求 5

**用户故事:** 作为用户，我希望删除摄像头时从数据库移除，以便清理不需要的配置。

#### 验收标准

1. WHEN 用户确认删除摄像头 THEN 系统 SHALL 从数据库中删除对应记录
2. WHEN 删除成功 THEN 界面 SHALL 立即移除该摄像头显示
3. WHEN 删除失败 THEN 系统 SHALL 显示错误信息并保持界面不变
4. WHEN 摄像头不存在 THEN 系统 SHALL 返回"未找到"错误
5. WHEN 删除操作 THEN 系统 SHALL 记录操作日志

### 需求 6

**用户故事:** 作为用户，我希望切换摄像头启用状态时更新数据库，以便状态持久化。

#### 验收标准

1. WHEN 用户切换摄像头开关 THEN 系统 SHALL 更新数据库中的 enabled 字段
2. WHEN 更新成功 THEN 界面 SHALL 立即反映新状态
3. WHEN 更新失败 THEN 开关 SHALL 恢复到原始状态
4. WHEN 批量切换多个摄像头 THEN 系统 SHALL 确保所有操作的原子性
5. WHEN 网络延迟 THEN 界面 SHALL 显示加载状态

### 需求 7

**用户故事:** 作为开发者，我希望实现 MVVM 架构，以便分离关注点并提高代码可维护性。

#### 验收标准

1. WHEN 组织代码 THEN Model层 SHALL 仅包含数据结构和数据库操作
2. WHEN 组织代码 THEN ViewModel层 SHALL 处理业务逻辑和数据转换
3. WHEN 组织代码 THEN View层 SHALL 仅负责 UI 渲染和用户交互
4. WHEN View层 需要数据 THEN View层 SHALL 通过 ViewModel 获取数据
5. WHEN Model层 数据变化 THEN ViewModel SHALL 通知 View 更新

### 需求 8

**用户故事:** 作为开发者，我希望建立前后端通信接口，以便 React 前端与 Python 后端交互。

#### 验收标准

1. WHEN 前端请求数据 THEN 系统 SHALL 通过 IPC 通道发送请求到后端
2. WHEN 后端接收请求 THEN 后端 SHALL 解析请求并调用相应的数据库操作
3. WHEN 后端处理完成 THEN 后端 SHALL 通过 IPC 返回结果给前端
4. WHEN 通信失败 THEN 系统 SHALL 重试最多 3 次
5. WHEN 请求超时 THEN 系统 SHALL 在 5 秒后返回超时错误

### 需求 9

**用户故事:** 作为用户，我希望摄像头状态实时更新，以便及时了解设备状态。

#### 验收标准

1. WHEN 摄像头状态变化 THEN 系统 SHALL 更新数据库中的 status 字段
2. WHEN 状态更新 THEN 界面 SHALL 在 1 秒内反映新状态
3. WHEN 多个摄像头同时变化 THEN 系统 SHALL 批量更新以提高性能
4. WHEN 后端检测到状态变化 THEN 后端 SHALL 主动推送更新到前端
5. WHERE 使用轮询机制 THEN 轮询间隔 SHALL 不超过 5 秒

### 需求 10

**用户故事:** 作为开发者，我希望实现数据验证机制，以便确保数据完整性和一致性。

#### 验收标准

1. WHEN 接收摄像头数据 THEN 系统 SHALL 验证所有必填字段存在
2. WHEN 验证 URL 格式 THEN 系统 SHALL 确保 URL 符合标准格式
3. WHEN 验证数值范围 THEN 系统 SHALL 确保 brightness 和 contrast 在 0-100 之间
4. WHEN 验证失败 THEN 系统 SHALL 返回详细的验证错误信息
5. WHEN 数据类型错误 THEN 系统 SHALL 拒绝操作并返回类型错误提示
