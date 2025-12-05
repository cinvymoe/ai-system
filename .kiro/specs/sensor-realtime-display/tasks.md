# Implementation Plan

- [x] 1. 创建TypeScript类型定义
  - 创建 src/types/sensor.ts 文件
  - 定义 SensorData 接口（加速度、角速度、角度）
  - 定义 MotionCommand 接口（命令、强度、时间戳）
  - 定义 MotionPattern 类型
  - 定义 SensorStreamMessage 接口（WebSocket消息格式）
  - 定义 ConnectionStatus 类型
  - _Requirements: 1.2, 1.3, 1.4, 2.1, 6.3_

- [x] 2. 创建后端WebSocket端点
  - 创建 backend/src/api/sensors.py 文件
  - 实现 /api/sensor/stream WebSocket端点
  - 集成 MockSensorDevice 创建和配置
  - 集成 MotionDirectionProcessor 数据处理
  - 实现数据流订阅和JSON消息推送
  - 处理客户端连接和断开事件
  - 添加错误处理和日志记录
  - _Requirements: 6.1, 6.3_

- [x] 2.1 实现运动模式切换端点
  - 在 backend/src/api/sensors.py 添加 POST /api/sensor/pattern 端点
  - 接收和验证运动模式参数
  - 更新 MockSensorDevice 的运动模式
  - 返回成功或错误响应
  - _Requirements: 8.2, 8.4_

- [x] 2.2 注册API路由
  - 在 backend/src/main.py 中注册 sensors 路由
  - 配置CORS允许WebSocket连接
  - 测试端点可访问性
  - _Requirements: 6.1_

- [x] 3. 创建useSensorStream自定义Hook
  - 创建 src/hooks/useSensorStream.ts 文件
  - 实现组件挂载时自动连接（useEffect）
  - 实现组件卸载时自动断开连接和清理资源
  - 实现WebSocket连接管理（内部自动管理）
  - 实现消息接收和解析逻辑
  - 实现自动重连机制（指数退避）
  - 实现延迟检测（2秒无数据显示警告）
  - 管理连接状态（disconnected, connecting, connected, error）
  - 提供 setMotionPattern 方法调用后端API
  - 返回传感器数据、运动指令、连接状态等
  - _Requirements: 3.1, 3.2, 5.2, 6.1, 6.2, 6.4, 6.5, 8.2_

- [x] 4. 创建数据格式化工具
  - 创建 src/utils/sensorDataFormatter.ts 文件
  - 实现数值格式化函数（保留2位小数）
  - 实现运动方向中文映射函数
  - 实现颜色编码映射函数
  - 实现时间戳格式化函数
  - _Requirements: 2.2, 2.3, 2.4, 2.5, 2.6, 5.1, 7.2, 7.3_

- [x] 5. 更新SensorSettings组件
  - 修改 src/components/settings/SensorSettings.tsx
  - 集成 useSensorStream Hook（进入页面自动订阅，离开自动取消）
  - 替换模拟数据为实时数据流
  - 显示连接状态指示器（无需手动控制按钮）
  - 显示实时传感器数据（加速度、角速度、角度）
  - 使用现有UI显示当前运动状态（接入后端运动方向数据）
  - 显示时间戳
  - 显示延迟警告（当适用时）
  - 添加运动模式选择器
  - 实现错误消息显示
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 3.1, 3.2, 3.3, 3.4, 3.5, 5.1, 5.2, 5.3, 8.1, 8.3_

- [x] 5.1 优化UI布局和样式
  - 实现数据分组显示（加速度、角速度、角度分开）
  - 应用颜色编码（绿色前进、红色后退、蓝色转向、灰色静止）
  - 使用等宽字体显示数值
  - 添加平滑过渡动画
  - 确保响应式布局
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ] 6. 手动测试和验证
  - 测试进入页面时自动连接
  - 测试离开页面时自动断开连接
  - 测试实时数据显示和更新
  - 测试所有运动模式（forward, backward, turn_left, turn_right, stationary）
  - 测试连接状态指示器
  - 测试自动重连机制
  - 测试延迟检测和警告
  - 测试运动模式切换
  - 测试错误处理和显示
  - 测试响应式布局
  - 测试数值格式化和颜色编码
  - 记录测试结果到文档
  - _Requirements: All_

