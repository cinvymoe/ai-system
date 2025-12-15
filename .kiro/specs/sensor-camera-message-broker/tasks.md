# Implementation Plan

- [x] 1. 创建消息代理核心模块结构
  - 创建 `backend/src/broker/` 目录
  - 创建 `__init__.py` 和基础模块文件
  - 定义数据模型（MessageData, ProcessedMessage, CameraInfo 等）
  - _Requirements: 1.1, 1.2_

- [x] 2. 实现 MessageBroker 单例类
  - 实现线程安全的单例模式
  - 实现消息类型注册机制
  - 实现订阅/取消订阅方法
  - 实现消息发布方法
  - _Requirements: 1.1, 1.3, 1.4, 1.5_

- [ ]* 2.1 编写 MessageBroker 单例属性测试
  - **Property 1: Singleton consistency**
  - **Validates: Requirements 1.1, 1.5**

- [ ]* 2.2 编写消息类型隔离属性测试
  - **Property 2: Message type isolation**
  - **Validates: Requirements 1.4**

- [x] 3. 实现 MessageTypeHandler 抽象基类和具体处理器
  - 创建 MessageTypeHandler 抽象基类
  - 实现 DirectionMessageHandler（方向消息处理）
  - 实现 AngleMessageHandler（角度消息处理）
  - 实现 AIAlertMessageHandler（AI 报警预留接口）
  - _Requirements: 2.1, 2.2, 3.1, 3.2, 7.1, 7.4_

- [ ]* 3.1 编写方向数据验证属性测试
  - **Property 3: Direction data validation**
  - **Validates: Requirements 2.2**

- [ ]* 3.2 编写角度范围验证属性测试
  - **Property 6: Angle range validation**
  - **Validates: Requirements 3.2**

- [x] 4. 实现 CameraMapper 摄像头映射器
  - 实现根据方向查询摄像头的方法
  - 实现根据角度查询摄像头的方法
  - 实现 AI 报警摄像头查询的预留方法
  - 处理空结果情况
  - _Requirements: 4.3, 4.4, 4.5, 5.3, 5.4, 5.5, 7.3_

- [ ]* 4.1 编写方向摄像头映射正确性属性测试
  - **Property 7: Direction camera mapping correctness**
  - **Validates: Requirements 4.3, 4.4**

- [ ]* 4.2 编写角度摄像头映射正确性属性测试
  - **Property 8: Angle camera mapping correctness**
  - **Validates: Requirements 5.3, 5.4**

- [x] 5. 实现订阅通知机制
  - 实现订阅者回调注册
  - 实现消息分发到所有订阅者
  - 实现订阅者错误隔离
  - 添加线程安全保护
  - _Requirements: 2.3, 3.3, 4.1, 4.2, 5.1, 5.2, 9.1, 9.2, 9.5_

- [ ]* 5.1 编写订阅者通知完整性属性测试
  - **Property 4: Subscriber notification completeness**
  - **Validates: Requirements 2.3, 3.3**

- [ ]* 5.2 编写消息顺序保持属性测试
  - **Property 5: Message ordering preservation**
  - **Validates: Requirements 2.5**

- [ ]* 5.3 编写订阅者失败隔离属性测试
  - **Property 10: Subscriber isolation on failure**
  - **Validates: Requirements 9.5**

- [ ]* 5.4 编写线程安全发布属性测试
  - **Property 11: Thread-safe publishing**
  - **Validates: Requirements 9.1**

- [x] 6. 实现错误处理机制
  - 创建 ErrorHandler 类
  - 实现验证错误处理
  - 实现数据库错误处理（重试机制）
  - 实现订阅者错误处理
  - _Requirements: 2.4, 3.5, 8.3_

- [x] 7. 实现日志记录功能
  - 配置结构化日志
  - 添加消息发布日志
  - 添加订阅注册日志
  - 添加错误日志
  - 实现可配置日志级别
  - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [x] 8. 实现动态消息类型注册
  - 支持运行时注册新消息类型
  - 支持自定义验证规则
  - 确保向后兼容性
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ]* 8.1 编写动态消息类型注册属性测试
  - **Property 9: Dynamic message type registration**
  - **Validates: Requirements 6.3, 6.5**

- [x] 9. 创建 WebSocket API 端点
  - 实现 `/api/broker/stream` WebSocket 端点
  - 实现连接时发送当前状态
  - 实现实时推送摄像头列表更新
  - 实现客户端断开处理
  - _Requirements: 10.1, 10.2, 10.4, 10.5_

- [ ]* 9.1 编写 WebSocket 广播一致性属性测试
  - **Property 12: WebSocket broadcast consistency**
  - **Validates: Requirements 10.2**

- [x] 10. 创建 HTTP API 端点
  - 实现 `/api/broker/mappings` GET 端点
  - 返回当前所有方向和角度的摄像头映射
  - _Requirements: 10.3_

- [x] 11. 集成消息代理到 FastAPI 应用
  - 在 `main.py` 的 lifespan 中初始化消息代理
  - 注册所有消息类型处理器
  - 创建 broker API 路由模块
  - 将路由添加到 FastAPI 应用
  - _Requirements: 1.2_

- [x] 12. 集成 MotionDirectionProcessor 与消息代理
  - 修改 `motion_processor.py`，在处理完成后发布方向消息
  - 确保消息格式符合 DirectionMessageHandler 的要求
  - _Requirements: 2.1, 2.3_

- [x] 13. 集成传感器 WebSocket 与消息代理
  - 修改 `sensors.py` API，在接收传感器数据后发布角度消息
  - 确保消息格式符合 AngleMessageHandler 的要求
  - _Requirements: 3.1, 3.3_

- [ ] 14. Checkpoint - 确保所有测试通过
  - 确保所有测试通过，如有问题请询问用户

- [ ]* 15. 编写集成测试
  - 测试端到端流程：传感器数据 → 消息代理 → 摄像头列表
  - 测试 WebSocket 实时推送
  - 测试 HTTP API 查询
  - _Requirements: All_

- [ ]* 16. 编写并发测试
  - 测试多线程发布场景
  - 测试多订阅者场景
  - 测试高频消息处理
  - _Requirements: 9.1, 9.2, 9.4_

- [ ] 17. 添加监控和可观测性
  - 实现指标收集（消息速率、订阅者数量、延迟）
  - 添加健康检查端点
  - 配置结构化日志输出
  - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [ ] 18. 创建使用文档和示例
  - 编写 README.md 说明消息代理的使用方法
  - 提供发布消息的示例代码
  - 提供订阅消息的示例代码
  - 提供 WebSocket 客户端示例
  - _Requirements: All_

- [ ] 19. Final Checkpoint - 确保所有测试通过
  - 确保所有测试通过，如有问题请询问用户
