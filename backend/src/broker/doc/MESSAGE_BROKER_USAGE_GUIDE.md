# MessageBroker 使用指南

## 概述

MessageBroker 是一个线程安全的单例消息代理系统，用于在系统各组件之间传递和处理消息。它支持消息类型注册、订阅/发布模式、以及自动的摄像头映射功能。

## 核心概念

### 1. 单例模式
MessageBroker 使用单例模式，确保全局只有一个实例。

### 2. 消息类型
系统支持三种预定义的消息类型：
- `direction_result` - 方向消息（前进、后退、左转、右转、静止）
- `angle_value` - 角度消息（角度值）
- `ai_alert` - AI 报警消息（预留接口）

### 3. 发布/订阅模式
- **发布者**：发布消息到特定类型
- **订阅者**：订阅特定类型的消息，接收通知

## 快速开始

### 1. 获取 MessageBroker 实例

```python
from broker.broker import MessageBroker

# 获取单例实例
broker = MessageBroker.get_instance()
```

### 2. 发布消息

```python
# 发布方向消息
result = broker.publish(
    message_type="direction_result",
    data={
        "command": "forward",
        "timestamp": "2024-01-01T12:00:00",
        "intensity": 0.8,
        "angular_intensity": 0.0
    }
)

print(f"发布成功: {result.success}")
print(f"消息ID: {result.message_id}")
print(f"通知订阅者数: {result.subscribers_notified}")
```

### 3. 订阅消息

```python
# 定义回调函数
def on_direction_message(message):
    print(f"收到方向消息: {message.data['command']}")
    print(f"消息ID: {message.message_id}")
    print(f"时间戳: {message.timestamp}")

# 订阅方向消息
subscription_id = broker.subscribe(
    message_type="direction_result",
    callback=on_direction_message
)

print(f"订阅ID: {subscription_id}")
```

### 4. 取消订阅

```python
# 取消订阅
success = broker.unsubscribe(
    message_type="direction_result",
    subscription_id=subscription_id
)

print(f"取消订阅成功: {success}")
```

## 详细用法

### 发布不同类型的消息

#### 方向消息 (direction_result)

```python
# 前进
broker.publish("direction_result", {
    "command": "forward",
    "timestamp": "2024-01-01T12:00:00",
    "intensity": 0.9,
    "angular_intensity": 0.0
})

# 左转
broker.publish("direction_result", {
    "command": "turn_left",
    "timestamp": "2024-01-01T12:00:01",
    "intensity": 0.5,
    "angular_intensity": 0.7
})

# 右转
broker.publish("direction_result", {
    "command": "turn_right",
    "timestamp": "2024-01-01T12:00:02",
    "intensity": 0.5,
    "angular_intensity": 0.7
})

# 后退
broker.publish("direction_result", {
    "command": "backward",
    "timestamp": "2024-01-01T12:00:03",
    "intensity": 0.6,
    "angular_intensity": 0.0
})

# 静止
broker.publish("direction_result", {
    "command": "stationary",
    "timestamp": "2024-01-01T12:00:04",
    "intensity": 0.0,
    "angular_intensity": 0.0
})
```

**必需字段：**
- `command`: 方向命令（forward, backward, turn_left, turn_right, stationary）
- `timestamp`: 时间戳（可选，默认使用当前时间）

**可选字段：**
- `intensity`: 强度值（0.0-1.0）
- `angular_intensity`: 角度强度（0.0-1.0）

#### 角度消息 (angle_value)

```python
# 发布角度消息
broker.publish("angle_value", {
    "angle": 45.5,
    "timestamp": "2024-01-01T12:00:00"
})
```

**必需字段：**
- `angle`: 角度值（-180.0 到 360.0）
- `timestamp`: 时间戳（可选）

#### AI 报警消息 (ai_alert)

```python
# 发布 AI 报警消息（预留接口）
broker.publish("ai_alert", {
    "alert_type": "motion_detected",
    "severity": "high",
    "timestamp": "2024-01-01T12:00:00",
    "metadata": {
        "camera_id": "cam_001",
        "confidence": 0.95
    }
})
```

**必需字段：**
- `alert_type`: 报警类型
- `severity`: 严重程度（low, medium, high, critical）
- `timestamp`: 时间戳（可选）

**可选字段：**
- `metadata`: 额外的元数据

### 订阅消息的高级用法

#### 订阅多种消息类型

```python
# 订阅方向消息
def on_direction(message):
    print(f"方向: {message.data['command']}")

direction_sub_id = broker.subscribe("direction_result", on_direction)

# 订阅角度消息
def on_angle(message):
    print(f"角度: {message.data['angle']}°")

angle_sub_id = broker.subscribe("angle_value", on_angle)

# 订阅 AI 报警
def on_alert(message):
    print(f"报警: {message.data['alert_type']} - {message.data['severity']}")

alert_sub_id = broker.subscribe("ai_alert", on_alert)
```

#### 使用类方法作为回调

```python
class MessageHandler:
    def __init__(self):
        self.message_count = 0
    
    def handle_direction(self, message):
        self.message_count += 1
        print(f"处理第 {self.message_count} 条方向消息")
        print(f"命令: {message.data['command']}")

# 创建处理器实例
handler = MessageHandler()

# 订阅消息
subscription_id = broker.subscribe(
    "direction_result",
    handler.handle_direction
)
```

#### 异步回调处理

```python
import asyncio

class AsyncMessageHandler:
    async def handle_message_async(self, message):
        # 异步处理消息
        await asyncio.sleep(0.1)
        print(f"异步处理完成: {message.message_id}")
    
    def handle_message(self, message):
        # 在回调中启动异步任务
        asyncio.create_task(self.handle_message_async(message))

handler = AsyncMessageHandler()
broker.subscribe("direction_result", handler.handle_message)
```

### 错误处理

#### 处理发布错误

```python
from broker.errors import PublishError

try:
    result = broker.publish("direction_result", {
        "command": "invalid_command"  # 无效命令
    })
    
    if not result.success:
        print(f"发布失败: {result.errors}")
        
except PublishError as e:
    print(f"发布错误: {e}")
```

#### 处理订阅错误

```python
from broker.errors import SubscriptionError

try:
    # 订阅不存在的消息类型
    subscription_id = broker.subscribe(
        "invalid_type",
        lambda msg: print(msg)
    )
except SubscriptionError as e:
    print(f"订阅错误: {e}")
```

#### 订阅者错误隔离

```python
# 即使某个订阅者出错，其他订阅者仍会收到消息

def good_subscriber(message):
    print(f"正常处理: {message.message_id}")

def bad_subscriber(message):
    raise Exception("订阅者处理错误")  # 这个错误不会影响其他订阅者

broker.subscribe("direction_result", good_subscriber)
broker.subscribe("direction_result", bad_subscriber)

# 发布消息 - good_subscriber 仍会收到消息
broker.publish("direction_result", {"command": "forward"})
```

## 与摄像头系统集成

### 自动摄像头映射

MessageBroker 会自动将消息映射到相关的摄像头：

```python
# 发布方向消息
result = broker.publish("direction_result", {
    "command": "forward"
})

# 系统会自动查找配置为 "forward" 方向的所有摄像头
# 并通过 WebSocket 推送给前端
```

### 查询摄像头映射

```python
# 获取摄像头映射器
camera_mapper = broker._camera_mapper

# 根据方向查询摄像头
cameras = camera_mapper.get_cameras_by_direction("forward")
for camera in cameras:
    print(f"摄像头: {camera.name} - {camera.url}")

# 根据角度查询摄像头
cameras = camera_mapper.get_cameras_by_angle(45.0)
for camera in cameras:
    print(f"摄像头: {camera.name} - 状态: {camera.status}")

# 获取所有方向的映射
all_mappings = camera_mapper.get_all_direction_mappings()
print(f"方向映射: {all_mappings}")

# 获取所有角度范围
angle_ranges = camera_mapper.get_all_angle_ranges()
print(f"角度范围: {angle_ranges}")
```

## WebSocket 实时推送

### WebSocket 端点工作原理

`@router.websocket("/stream")` 端点实现了完整的订阅-发布-广播机制：

#### 1. 连接建立流程

```python
@router.websocket("/stream")
async def broker_stream(websocket: WebSocket):
    # 1. 初始化 MessageBroker（如果尚未初始化）
    await _initialize_broker()
    
    # 2. 接受 WebSocket 连接
    await connection_manager.connect(websocket)
    
    # 3. 发送当前状态（所有方向和角度的摄像头映射）
    await _send_current_state(websocket)
    
    # 4. 保持连接，等待消息广播
    while True:
        message = await websocket.receive_text()
        # 处理客户端消息（如 "refresh" 命令）
```

#### 2. 订阅消息类型

在 `_initialize_broker()` 中，系统自动订阅三种消息类型：

```python
async def _initialize_broker():
    broker = MessageBroker.get_instance()
    
    # 注册消息类型处理器
    broker.register_message_type("direction_result", DirectionMessageHandler())
    broker.register_message_type("angle_value", AngleMessageHandler())
    broker.register_message_type("ai_alert", AIAlertMessageHandler())
    
    # 为每种消息类型注册广播回调
    for message_type in ["direction_result", "angle_value", "ai_alert"]:
        callback = create_broadcast_callback(message_type)
        broker.subscribe(message_type, callback)
```

#### 3. 回调处理机制

当有消息发布时，`broadcast_callback` 会被触发：

```python
def create_broadcast_callback(message_type: str):
    async def broadcast_callback(message: MessageData):
        # 步骤 1: 根据消息获取匹配的摄像头列表
        cameras = await _get_cameras_for_message(message)
        
        # 步骤 2: 构建广播消息（包含报警类型和摄像头列表）
        broadcast_message = {
            "type": message

### HTTP API 查询

```bash
# 查询当前摄像头映射
curl http://localhost:8000/api/broker/mappings

# 查询 Broker 状态
curl http://localhost:8000/api/broker/status

# 测试发布消息
curl -X POST "http://localhost:8000/api/broker/test/publish?message_type=direction_result" \
  -H "Content-Type: application/json" \
  -d '{"command": "forward", "intensity": 0.9}'

# 获取 Broker 详细信息
curl http://localhost:8000/api/broker/test/info
```

## 统计信息和监控

### 获取统计信息

```python
# 获取统计信息
stats = broker.get_stats()
print(f"已发布消息数: {stats['messages_published']}")
print(f"失败消息数: {stats['messages_failed']}")
print(f"订阅者总数: {stats['subscribers_count']}")

# 获取已注册的消息类型
types = broker.get_registered_types()
print(f"已注册类型: {types}")

# 获取特定类型的订阅者数量
count = broker.get_subscriber_count("direction_result")
print(f"方向消息订阅者数: {count}")

# 获取所有订阅者数量
total = broker.get_subscriber_count()
print(f"总订阅者数: {total}")
```

### 检查消息类型是否已注册

```python
# 检查消息类型
if broker.is_type_registered("direction_result"):
    print("方向消息类型已注册")

# 获取处理器
handler = broker.get_handler("direction_result")
print(f"处理器类型: {handler.__class__.__name__}")
```

## 高级功能

### 动态注册新消息类型

```python
from broker.handlers import MessageTypeHandler
from broker.models import ValidationResult, ProcessedMessage, MessageData
from datetime import datetime

# 创建自定义消息处理器
class CustomMessageHandler(MessageTypeHandler):
    def validate(self, data):
        errors = []
        if 'custom_field' not in data:
            errors.append("Missing required field: custom_field")
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=[]
        )
    
    def process(self, data):
        processed_data = {
            'custom_field': data['custom_field'],
            'timestamp': data.get('timestamp', datetime.now().isoformat())
        }
        
        message = MessageData(
            type=self.get_type_name(),
            data=processed_data,
            timestamp=datetime.now()
        )
        
        return ProcessedMessage(
            original=message,
            validated=True,
            cameras=[],
            processing_time=0.0,
            errors=[]
        )
    
    def get_type_name(self):
        return "custom_message"

# 注册新消息类型
broker.register_message_type(
    "custom_message",
    CustomMessageHandler()
)

# 使用新消息类型
broker.subscribe("custom_message", lambda msg: print(f"自定义消息: {msg.data}"))
broker.publish("custom_message", {"custom_field": "test_value"})
```

### 注销消息类型

```python
# 注销消息类型（订阅者列表会保留）
success = broker.unregister_message_type("custom_message")
print(f"注销成功: {success}")
```

### 资源清理

```python
# 关闭 MessageBroker，清理所有资源
broker.shutdown()
```

## 最佳实践

### 1. 使用单例模式

```python
# ✅ 正确：使用 get_instance()
broker = MessageBroker.get_instance()

# ❌ 错误：不要直接实例化
# broker = MessageBroker()  # 会抛出 RuntimeError
```

### 2. 错误处理

```python
# ✅ 正确：检查发布结果
result = broker.publish("direction_result", data)
if not result.success:
    logger.error(f"发布失败: {result.errors}")

# ✅ 正确：订阅者中处理异常
def safe_callback(message):
    try:
        # 处理消息
        process_message(message)
    except Exception as e:
        logger.error(f"处理消息失败: {e}")
```

### 3. 订阅管理

```python
# ✅ 正确：保存订阅 ID 以便后续取消
subscription_ids = []

def setup_subscriptions():
    sub_id = broker.subscribe("direction_result", on_direction)
    subscription_ids.append(sub_id)

def cleanup_subscriptions():
    for sub_id in subscription_ids:
        broker.unsubscribe("direction_result", sub_id)
```

### 4. 线程安全

```python
# ✅ MessageBroker 是线程安全的，可以在多线程环境中使用
import threading

def worker():
    broker = MessageBroker.get_instance()
    broker.publish("direction_result", {"command": "forward"})

threads = [threading.Thread(target=worker) for _ in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()
```

### 5. 消息验证

```python
# ✅ 正确：提供完整的必需字段
broker.publish("direction_result", {
    "command": "forward",
    "timestamp": datetime.now().isoformat(),
    "intensity": 0.8
})

# ❌ 错误：缺少必需字段
# broker.publish("direction_result", {})  # 验证失败
```

## 常见问题

### Q1: 如何确保消息按顺序处理？

A: MessageBroker 保证同一消息类型的订阅者按注册顺序接收消息。

### Q2: 订阅者回调函数出错会影响其他订阅者吗？

A: 不会。MessageBroker 实现了订阅者错误隔离，一个订阅者的错误不会影响其他订阅者。

### Q3: 可以在回调函数中发布新消息吗？

A: 可以，但要注意避免循环发布导致的无限递归。

### Q4: MessageBroker 是否支持异步操作？

A: MessageBroker 本身是同步的，但可以在回调函数中启动异步任务。

### Q5: 如何监控 MessageBroker 的性能？

A: 使用 `get_stats()` 方法获取统计信息，包括消息数量、订阅者数量等。

## 完整示例

### 传感器数据处理系统

```python
from broker.broker import MessageBroker
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 获取 MessageBroker 实例
broker = MessageBroker.get_instance()

# 1. 定义消息处理器
class SensorDataProcessor:
    def __init__(self):
        self.direction_count = 0
        self.angle_count = 0
    
    def process_direction(self, message):
        """处理方向消息"""
        self.direction_count += 1
        command = message.data['command']
        intensity = message.data.get('intensity', 0.0)
        
        logger.info(
            f"[{self.direction_count}] 方向: {command}, "
            f"强度: {intensity:.2f}"
        )
    
    def process_angle(self, message):
        """处理角度消息"""
        self.angle_count += 1
        angle = message.data['angle']
        
        logger.info(
            f"[{self.angle_count}] 角度: {angle:.1f}°"
        )

# 2. 创建处理器并订阅消息
processor = SensorDataProcessor()

direction_sub = broker.subscribe(
    "direction_result",
    processor.process_direction
)

angle_sub = broker.subscribe(
    "angle_value",
    processor.process_angle
)

logger.info("订阅完成，开始发布消息...")

# 3. 模拟传感器数据
sensor_data = [
    ("direction_result", {"command": "forward", "intensity": 0.9}),
    ("angle_value", {"angle": 45.0}),
    ("direction_result", {"command": "turn_left", "intensity": 0.7}),
    ("angle_value", {"angle": 90.0}),
    ("direction_result", {"command": "backward", "intensity": 0.6}),
]

# 4. 发布消息
for msg_type, data in sensor_data:
    data['timestamp'] = datetime.now().isoformat()
    result = broker.publish(msg_type, data)
    
    if result.success:
        logger.info(
            f"✓ 发布成功: {msg_type}, "
            f"通知 {result.subscribers_notified} 个订阅者"
        )
    else:
        logger.error(f"✗ 发布失败: {result.errors}")

# 5. 显示统计信息
stats = broker.get_stats()
logger.info(f"\n统计信息:")
logger.info(f"  已发布消息: {stats['messages_published']}")
logger.info(f"  失败消息: {stats['messages_failed']}")
logger.info(f"  订阅者总数: {stats['subscribers_count']}")

# 6. 清理
broker.unsubscribe("direction_result", direction_sub)
broker.unsubscribe("angle_value", angle_sub)
logger.info("清理完成")
```

## 相关文档

- [Broker Implementation Summary](./BROKER_IMPLEMENTATION_SUMMARY.md) - 实现细节
- [Dynamic Registration Guide](./DYNAMIC_REGISTRATION_GUIDE.md) - 动态注册指南
- [Subscription Notification Guide](./SUBSCRIPTION_NOTIFICATION_GUIDE.md) - 订阅通知指南
- [Error Handler Guide](./ERROR_HANDLER_GUIDE.md) - 错误处理指南

## 技术支持

如有问题，请查看：
- 测试文件：`backend/test_broker_*.py`
- API 文档：`backend/src/api/broker.py`
- 核心实现：`backend/src/broker/broker.py`
