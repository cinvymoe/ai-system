# Design Document: Sensor-Camera Message Broker

## Overview

传感器-摄像头消息代理系统是一个全局消息处理模块，负责订阅传感器数据（方向处理结果和角度值），并将这些数据映射到对应的摄像头地址列表。系统采用发布-订阅（Pub-Sub）模式，提供可扩展的架构以支持未来添加新的消息类型（如 AI 报警）。

该系统作为后端的核心消息总线，连接传感器数据处理层和摄像头管理层，实现数据驱动的摄像头调度。

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (WebSocket)                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  WebSocket API Layer                         │
│  - /api/broker/stream (WebSocket)                           │
│  - /api/broker/mappings (HTTP GET)                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Message Broker (Singleton)                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Message Type Registry                               │   │
│  │  - direction_result                                  │   │
│  │  - angle_value                                       │   │
│  │  - ai_alert (placeholder)                            │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Subscription Manager                                │   │
│  │  - Subscriber callbacks per message type             │   │
│  │  - Thread-safe registration/unregistration           │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Camera Mapper                                       │   │
│  │  - Direction → Camera URLs                           │   │
│  │  - Angle → Camera URLs                               │   │
│  │  - AI Alert → Camera URLs (placeholder)              │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  Motion     │  │   Sensor    │  │  AI System  │
│  Processor  │  │   Collector │  │  (Future)   │
│  (Publisher)│  │  (Publisher)│  │  (Publisher)│
└─────────────┘  └─────────────┘  └─────────────┘
         │               │               │
         └───────────────┼───────────────┘
                         ▼
                ┌─────────────────┐
                │    Database     │
                │  - cameras      │
                │  - angle_ranges │
                └─────────────────┘
```

### Design Patterns

1. **Singleton Pattern**: Message Broker 使用单例模式确保全局唯一实例
2. **Publish-Subscribe Pattern**: 解耦消息发布者和订阅者
3. **Strategy Pattern**: 每种消息类型有独立的验证和处理策略
4. **Observer Pattern**: 订阅者观察消息变化并响应

## Components and Interfaces

### 1. Message Broker Core

```python
class MessageBroker:
    """全局消息代理（单例）"""
    
    _instance: Optional['MessageBroker'] = None
    _lock: threading.Lock = threading.Lock()
    
    @classmethod
    def get_instance(cls) -> 'MessageBroker':
        """获取单例实例"""
        
    def __init__(self):
        self._message_types: Dict[str, MessageTypeHandler] = {}
        self._subscribers: Dict[str, List[Callable]] = {}
        self._camera_mapper: CameraMapper = CameraMapper()
        self._logger: logging.Logger = logging.getLogger(__name__)
        self._subscription_lock: threading.RLock = threading.RLock()
        
    def register_message_type(
        self, 
        message_type: str, 
        handler: MessageTypeHandler
    ) -> None:
        """注册新的消息类型"""
        
    def publish(
        self, 
        message_type: str, 
        data: Dict[str, Any]
    ) -> PublishResult:
        """发布消息"""
        
    def subscribe(
        self, 
        message_type: str, 
        callback: Callable[[MessageData], None]
    ) -> str:
        """订阅消息类型，返回订阅ID"""
        
    def unsubscribe(
        self, 
        message_type: str, 
        subscription_id: str
    ) -> bool:
        """取消订阅"""
```

### 2. Message Type Handler

```python
class MessageTypeHandler(ABC):
    """消息类型处理器抽象基类"""
    
    @abstractmethod
    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """验证消息数据"""
        
    @abstractmethod
    def process(self, data: Dict[str, Any]) -> ProcessedMessage:
        """处理消息数据"""
        
    @abstractmethod
    def get_type_name(self) -> str:
        """获取消息类型名称"""


class DirectionMessageHandler(MessageTypeHandler):
    """方向消息处理器"""
    
    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        # 验证必需字段: command, timestamp
        # 验证 command 值: forward, backward, turn_left, turn_right, stationary
        
    def process(self, data: Dict[str, Any]) -> ProcessedMessage:
        # 提取方向信息
        # 返回标准化的消息对象


class AngleMessageHandler(MessageTypeHandler):
    """角度消息处理器"""
    
    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        # 验证必需字段: angle, timestamp
        # 验证角度范围: -180 到 180 或 0 到 360
        
    def process(self, data: Dict[str, Any]) -> ProcessedMessage:
        # 提取角度信息
        # 返回标准化的消息对象


class AIAlertMessageHandler(MessageTypeHandler):
    """AI 报警消息处理器（预留）"""
    
    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        # 验证必需字段: alert_type, severity, timestamp
        # 验证 severity: low, medium, high, critical
        
    def process(self, data: Dict[str, Any]) -> ProcessedMessage:
        # 提取报警信息
        # 返回标准化的消息对象
```

### 3. Camera Mapper

```python
class CameraMapper:
    """摄像头映射器 - 将消息数据映射到摄像头列表"""
    
    def __init__(self, db_session_factory: Callable[[], Session]):
        self._db_session_factory = db_session_factory
        
    def get_cameras_by_direction(
        self, 
        direction: str
    ) -> List[CameraInfo]:
        """根据方向获取摄像头列表"""
        # 查询 cameras 表，筛选 directions 字段包含该方向的摄像头
        # 返回摄像头 URL 列表
        
    def get_cameras_by_angle(
        self, 
        angle: float
    ) -> List[CameraInfo]:
        """根据角度获取摄像头列表"""
        # 查询 angle_ranges 表，找到包含该角度的范围
        # 获取该范围关联的摄像头 ID
        # 查询 cameras 表获取摄像头详情
        # 返回摄像头 URL 列表
        
    def get_cameras_by_ai_alert(
        self, 
        alert_data: Dict[str, Any]
    ) -> List[CameraInfo]:
        """根据 AI 报警获取摄像头列表（预留）"""
        # 未来实现：根据报警类型和位置信息查询相关摄像头
        # 当前返回空列表
```

### 4. WebSocket API

```python
@router.websocket("/api/broker/stream")
async def broker_stream(websocket: WebSocket):
    """WebSocket 端点 - 实时推送摄像头列表更新"""
    await websocket.accept()
    
    # 发送当前状态
    current_state = broker.get_current_state()
    await websocket.send_json(current_state)
    
    # 订阅消息更新
    def on_message(message_data: MessageData):
        # 获取对应的摄像头列表
        cameras = broker.get_cameras_for_message(message_data)
        # 通过 WebSocket 发送
        asyncio.create_task(
            websocket.send_json({
                "type": message_data.type,
                "cameras": cameras,
                "timestamp": message_data.timestamp
            })
        )
    
    subscription_id = broker.subscribe("*", on_message)
    
    try:
        while True:
            # 保持连接
            await websocket.receive_text()
    finally:
        broker.unsubscribe("*", subscription_id)


@router.get("/api/broker/mappings")
async def get_current_mappings():
    """HTTP 端点 - 查询当前摄像头映射"""
    return {
        "directions": broker.get_all_direction_mappings(),
        "angles": broker.get_all_angle_mappings(),
        "timestamp": datetime.now().isoformat()
    }
```

## Data Models

### Message Data Models

```python
@dataclass
class MessageData:
    """消息数据"""
    type: str  # 消息类型
    data: Dict[str, Any]  # 消息内容
    timestamp: datetime
    message_id: str  # 唯一消息ID


@dataclass
class ProcessedMessage:
    """处理后的消息"""
    original: MessageData
    validated: bool
    cameras: List[CameraInfo]
    processing_time: float
    errors: List[str]


@dataclass
class CameraInfo:
    """摄像头信息"""
    id: str
    name: str
    url: str
    status: str  # online/offline
    directions: List[str]  # 关联的方向


@dataclass
class PublishResult:
    """发布结果"""
    success: bool
    message_id: str
    subscribers_notified: int
    errors: List[str]


@dataclass
class ValidationResult:
    """验证结果"""
    valid: bool
    errors: List[str]
    warnings: List[str]
```

### Database Models

使用现有的数据库模型：
- `Camera`: 摄像头表（已存在）
- `AngleRange`: 角度范围表（已存在）

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Singleton consistency
*For any* two requests for the Message Broker instance, they should return the same object reference
**Validates: Requirements 1.1, 1.5**

### Property 2: Message type isolation
*For any* two different message types, subscribers to one type should not receive messages from the other type
**Validates: Requirements 1.4**

### Property 3: Direction data validation
*For any* direction message with missing required fields, the broker should reject it
**Validates: Requirements 2.2**

### Property 4: Subscriber notification completeness
*For any* published message, all registered subscribers for that message type should be notified
**Validates: Requirements 2.3, 3.3**

### Property 5: Message ordering preservation
*For any* sequence of messages published in order, subscribers should receive them in the same order
**Validates: Requirements 2.5**

### Property 6: Angle range validation
*For any* angle value outside the valid range (-180 to 180), the broker should reject it
**Validates: Requirements 3.2**

### Property 7: Direction camera mapping correctness
*For any* direction value, the returned camera list should only contain cameras whose directions field includes that direction
**Validates: Requirements 4.3, 4.4**

### Property 8: Angle camera mapping correctness
*For any* angle value, the returned camera list should only contain cameras associated with angle ranges that include that angle
**Validates: Requirements 5.3, 5.4**

### Property 9: Dynamic message type registration
*For any* new message type registered at runtime, it should be immediately available for publishing and subscription without affecting existing types
**Validates: Requirements 6.3, 6.5**

### Property 10: Subscriber isolation on failure
*For any* subscriber callback that throws an exception, other subscribers should still receive the message
**Validates: Requirements 9.5**

### Property 11: Thread-safe publishing
*For any* concurrent publishing operations from multiple threads, all messages should be processed without data corruption
**Validates: Requirements 9.1**

### Property 12: WebSocket broadcast consistency
*For any* message published to the broker, all connected WebSocket clients should receive the corresponding camera list update
**Validates: Requirements 10.2**

## Error Handling

### Error Categories

1. **Validation Errors**
   - 缺少必需字段
   - 数据类型不匹配
   - 值超出有效范围
   - 处理：拒绝消息，记录错误日志，返回错误详情

2. **Database Errors**
   - 连接失败
   - 查询超时
   - 数据不一致
   - 处理：重试机制，降级处理（返回缓存数据），记录错误日志

3. **Subscriber Errors**
   - 回调函数异常
   - 回调超时
   - 处理：隔离错误，不影响其他订阅者，记录错误日志

4. **WebSocket Errors**
   - 连接断开
   - 发送失败
   - 处理：自动清理断开的连接，不影响消息处理

### Error Recovery Strategies

```python
class ErrorHandler:
    """错误处理器"""
    
    def handle_validation_error(
        self, 
        message: MessageData, 
        error: ValidationResult
    ) -> None:
        """处理验证错误"""
        self._logger.error(
            f"Validation failed for message {message.message_id}: "
            f"{error.errors}"
        )
        # 不重试，直接拒绝
        
    def handle_database_error(
        self, 
        operation: str, 
        error: Exception
    ) -> Optional[Any]:
        """处理数据库错误"""
        self._logger.error(f"Database error in {operation}: {error}")
        # 尝试重试
        for attempt in range(3):
            try:
                return self._retry_operation(operation)
            except Exception:
                if attempt == 2:
                    # 最后一次失败，返回缓存或空结果
                    return self._get_cached_result(operation)
                time.sleep(0.1 * (attempt + 1))
                
    def handle_subscriber_error(
        self, 
        subscriber_id: str, 
        error: Exception
    ) -> None:
        """处理订阅者错误"""
        self._logger.error(
            f"Subscriber {subscriber_id} callback failed: {error}"
        )
        # 记录错误但继续处理其他订阅者
```

## Testing Strategy

### Unit Testing

使用 pytest 进行单元测试，覆盖以下场景：

1. **Message Broker Core**
   - 单例模式验证
   - 消息类型注册
   - 发布/订阅机制
   - 取消订阅

2. **Message Handlers**
   - 数据验证逻辑
   - 消息处理逻辑
   - 错误处理

3. **Camera Mapper**
   - 方向映射查询
   - 角度映射查询
   - 空结果处理

4. **WebSocket API**
   - 连接建立
   - 消息广播
   - 断开处理

### Property-Based Testing

使用 Hypothesis 库进行属性测试，配置每个测试运行至少 100 次迭代。

每个属性测试必须使用以下格式标注：
```python
# Feature: sensor-camera-message-broker, Property {number}: {property_text}
```

**测试库选择**: Hypothesis (Python)

**配置要求**:
- 每个属性测试至少运行 100 次迭代
- 使用 `@given` 装饰器定义输入生成策略
- 使用 `@settings(max_examples=100)` 配置迭代次数

### Integration Testing

1. **端到端流程测试**
   - 传感器数据 → 消息代理 → 摄像头列表
   - WebSocket 实时推送
   - HTTP API 查询

2. **并发测试**
   - 多线程发布
   - 多订阅者场景
   - 高频消息处理

3. **数据库集成测试**
   - 摄像头查询
   - 角度范围查询
   - 事务处理

### Performance Testing

1. **吞吐量测试**
   - 每秒处理消息数
   - 订阅者数量对性能的影响

2. **延迟测试**
   - 消息发布到订阅者接收的延迟
   - WebSocket 推送延迟

3. **资源使用测试**
   - 内存占用
   - CPU 使用率
   - 数据库连接池

## Implementation Notes

### Initialization

在 FastAPI 应用启动时初始化消息代理：

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 初始化消息代理
    broker = MessageBroker.get_instance()
    
    # 注册消息类型
    broker.register_message_type(
        "direction_result", 
        DirectionMessageHandler()
    )
    broker.register_message_type(
        "angle_value", 
        AngleMessageHandler()
    )
    broker.register_message_type(
        "ai_alert", 
        AIAlertMessageHandler()  # 预留
    )
    
    # 订阅传感器数据（从现有的传感器 API 集成）
    # 这将在传感器 API 中调用 broker.publish()
    
    yield
    
    # 清理资源
    broker.shutdown()
```

### Integration with Existing Code

1. **与 MotionDirectionProcessor 集成**
   ```python
   # 在 motion_processor.py 中
   def process(self, sensor_data: Dict[str, Any]) -> MotionCommand:
       motion_command = # ... 现有处理逻辑
       
       # 发布到消息代理
       broker = MessageBroker.get_instance()
       broker.publish("direction_result", {
           "command": motion_command.command,
           "intensity": motion_command.intensity,
           "timestamp": motion_command.timestamp.isoformat()
       })
       
       return motion_command
   ```

2. **与传感器 WebSocket 集成**
   ```python
   # 在 sensors.py API 中
   @router.websocket("/api/sensor/stream")
   async def sensor_stream(websocket: WebSocket):
       # ... 现有代码
       
       # 发布角度数据到消息代理
       broker = MessageBroker.get_instance()
       broker.publish("angle_value", {
           "angle": sensor_data["角度Z(°)"],
           "timestamp": datetime.now().isoformat()
       })
   ```

### Extensibility for AI Alerts

预留的 AI 报警接口设计：

```python
# 未来 AI 系统集成示例
def on_ai_detection(detection_result: Dict[str, Any]):
    broker = MessageBroker.get_instance()
    broker.publish("ai_alert", {
        "alert_type": "person_detected",
        "severity": "high",
        "location": detection_result["location"],
        "confidence": detection_result["confidence"],
        "timestamp": datetime.now().isoformat(),
        "camera_id": detection_result["camera_id"]
    })
```

## Security Considerations

1. **输入验证**: 所有消息数据必须经过严格验证
2. **访问控制**: WebSocket 连接应该需要认证（未来实现）
3. **日志脱敏**: 敏感信息（如摄像头密码）不应记录到日志
4. **资源限制**: 限制订阅者数量和消息队列大小，防止资源耗尽

## Monitoring and Observability

1. **指标收集**
   - 消息发布速率
   - 订阅者数量
   - 处理延迟
   - 错误率

2. **日志记录**
   - 结构化日志（JSON 格式）
   - 日志级别：DEBUG, INFO, WARNING, ERROR, CRITICAL
   - 包含上下文信息：message_id, message_type, timestamp

3. **健康检查**
   - 消息代理状态
   - 数据库连接状态
   - WebSocket 连接数
