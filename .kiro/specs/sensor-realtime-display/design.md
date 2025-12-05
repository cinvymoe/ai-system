# Design Document

## Overview

本设计文档描述了前端9轴传感器实时显示界面的架构和实现细节。该界面将集成到现有的SensorSettings组件中，通过WebSocket或HTTP轮询订阅后端mock_sensor的实时数据流，显示原始传感器数据（加速度、角速度、角度）和处理后的运动方向结果（前进、后退、左转、右转、静止）。

系统采用React + TypeScript实现，使用现有的UI组件库，并通过FastAPI后端提供的WebSocket端点进行实时数据通信。

## Architecture

系统采用前后端分离的实时数据流架构：

```
┌─────────────────────────────────────────┐
│   Frontend (React + TypeScript)         │
│                                          │
│   ┌──────────────────────────────────┐  │
│   │  SensorSettings Component        │  │
│   │  - 显示实时传感器数据             │  │
│   │  - 显示运动方向                   │  │
│   │  - 控制连接状态                   │  │
│   │  - 选择运动模式                   │  │
│   └──────────┬───────────────────────┘  │
│              │                           │
│   ┌──────────▼───────────────────────┐  │
│   │  useSensorStream Hook            │  │
│   │  - WebSocket连接管理              │  │
│   │  - 数据订阅和解析                 │  │
│   │  - 自动重连                       │  │
│   └──────────┬───────────────────────┘  │
└──────────────┼───────────────────────────┘
               │ WebSocket/HTTP
┌──────────────▼───────────────────────────┐
│   Backend (FastAPI)                      │
│                                          │
│   ┌──────────────────────────────────┐  │
│   │  /api/sensor/stream (WebSocket)  │  │
│   │  - 推送实时传感器数据             │  │
│   │  - 推送运动指令                   │  │
│   └──────────┬───────────────────────┘  │
│              │                           │
│   ┌──────────▼───────────────────────┐  │
│   │  MockSensorDevice                │  │
│   │  - 生成模拟传感器数据             │  │
│   └──────────┬───────────────────────┘  │
│              │                           │
│   ┌──────────▼───────────────────────┐  │
│   │  MotionDirectionProcessor        │  │
│   │  - 分析传感器数据                 │  │
│   │  - 输出运动指令                   │  │
│   └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

## Components and Interfaces

### 1. SensorSettings Component (Enhanced)

**位置**: `src/components/settings/SensorSettings.tsx`

**职责**:
- 显示实时传感器数据（加速度、角速度、角度）
- 显示处理后的运动方向和强度
- 提供连接控制（开始/停止订阅）
- 显示连接状态和时间戳
- 提供运动模式选择器
- 处理错误和延迟警告

**Props**:
```typescript
interface SensorSettingsProps {
  onBack: () => void;
  currentDirection: Direction;
}
```

**State**:
```typescript
interface SensorState {
  // 连接状态（自动管理，无需手动控制）
  isConnected: boolean;
  connectionStatus: 'disconnected' | 'connecting' | 'connected' | 'error';
  
  // 传感器数据
  sensorData: {
    acceleration: { x: number; y: number; z: number };
    angularVelocity: { x: number; y: number; z: number };
    angles: { x: number; y: number; z: number };
  } | null;
  
  // 运动指令
  motionCommand: {
    command: 'forward' | 'backward' | 'turn_left' | 'turn_right' | 'stationary';
    intensity: number;
    angularIntensity: number;
    timestamp: string;
  } | null;
  
  // 运动模式
  motionPattern: string;
  
  // 错误和警告
  error: string | null;
  isDelayed: boolean;
  lastUpdateTime: Date | null;
}
```

### 2. useSensorStream Hook

**位置**: `src/hooks/useSensorStream.ts` (新建)

**职责**:
- 管理WebSocket连接生命周期
- 订阅和解析实时数据流
- 实现自动重连机制（指数退避）
- 处理连接错误和超时
- 提供连接控制方法

**接口**:
```typescript
interface UseSensorStreamOptions {
  autoConnect?: boolean;  // 默认true，组件挂载时自动连接
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

interface UseSensorStreamReturn {
  // 状态
  isConnected: boolean;
  connectionStatus: 'disconnected' | 'connecting' | 'connected' | 'error';
  sensorData: SensorData | null;
  motionCommand: MotionCommand | null;
  error: string | null;
  lastUpdateTime: Date | null;
  
  // 控制方法（内部自动管理，组件卸载时自动断开）
  setMotionPattern: (pattern: string) => Promise<void>;
}

function useSensorStream(options?: UseSensorStreamOptions): UseSensorStreamReturn
```

### 3. Backend WebSocket Endpoint

**位置**: `backend/src/api/sensors.py` (新建)

**职责**:
- 提供WebSocket端点 `/api/sensor/stream`
- 从MockSensorDevice订阅数据流
- 通过MotionDirectionProcessor处理数据
- 推送JSON格式的实时数据到前端
- 处理客户端连接和断开

**端点**:
```python
@router.websocket("/api/sensor/stream")
async def sensor_stream_websocket(websocket: WebSocket):
    """
    WebSocket端点，推送实时传感器数据和运动指令
    """
    await websocket.accept()
    
    # 创建MockSensorDevice和MotionDirectionProcessor
    # 订阅数据流
    # 持续推送数据直到连接关闭
```

**数据格式**:
```typescript
interface SensorStreamMessage {
  type: 'sensor_data' | 'motion_command' | 'error';
  timestamp: string;
  data: {
    // sensor_data类型
    acceleration?: { x: number; y: number; z: number };
    angularVelocity?: { x: number; y: number; z: number };
    angles?: { x: number; y: number; z: number };
    temperature?: number;
    battery?: number;
    
    // motion_command类型
    command?: string;
    intensity?: number;
    angularIntensity?: number;
    rawDirection?: string;
    isMotionStart?: boolean;
    
    // error类型
    error?: string;
  };
}
```

### 4. Backend Pattern Control Endpoint

**位置**: `backend/src/api/sensors.py`

**职责**:
- 提供HTTP POST端点 `/api/sensor/pattern`
- 接收运动模式切换请求
- 更新MockSensorDevice的运动模式

**端点**:
```python
@router.post("/api/sensor/pattern")
async def set_motion_pattern(pattern: str):
    """
    设置mock sensor的运动模式
    """
    # 验证pattern有效性
    # 更新MockSensorDevice的motion_pattern
    # 返回成功响应
```

## Data Models

### Frontend Data Models

```typescript
// 传感器数据
interface SensorData {
  acceleration: {
    x: number;  // g
    y: number;  // g
    z: number;  // g
  };
  angularVelocity: {
    x: number;  // °/s
    y: number;  // °/s
    z: number;  // °/s
  };
  angles: {
    x: number;  // °
    y: number;  // °
    z: number;  // °
  };
  temperature: number;  // °C
  battery: number;  // %
  timestamp: string;
}

// 运动指令
interface MotionCommand {
  command: 'forward' | 'backward' | 'turn_left' | 'turn_right' | 'stationary';
  intensity: number;  // 线性运动强度
  angularIntensity: number;  // 角度运动强度
  rawDirection: string;  // 原始方向字符串
  isMotionStart: boolean;  // 是否是运动开始
  timestamp: string;
}

// 运动模式
type MotionPattern = 'forward' | 'backward' | 'turn_left' | 'turn_right' | 'stationary';
```

### Backend Data Models

后端使用现有的数据模型：
- `CollectedData`: 传感器采集数据
- `MotionCommand`: 运动指令（已在 `backend/src/collectors/models.py` 中定义）

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Data display responsiveness

*For any* sensor data update received from the backend, the frontend SHALL refresh the displayed values within 200ms.

**Validates: Requirements 1.5**

### Property 2: Motion direction visual consistency

*For any* motion command received, the system SHALL display the correct Chinese label and color coding:
- forward → "前进" with green indicator
- backward → "后退" with red indicator
- turn_left → "左转" with blue indicator
- turn_right → "右转" with blue indicator
- stationary → "静止" with gray indicator

**Validates: Requirements 2.2, 2.3, 2.4, 2.5, 2.6**

### Property 3: Connection state consistency

*For any* connection state change, the displayed status indicator SHALL accurately reflect the current state (连接中/已断开/错误).

**Validates: Requirements 3.3, 3.4**

### Property 4: Data format precision

*For any* numeric sensor value displayed, the system SHALL format the number to exactly 2 decimal places.

**Validates: Requirements 7.2**

### Property 5: Delay detection

*For any* time period where no data is received for 2 seconds or more, the system SHALL display a "数据延迟" warning.

**Validates: Requirements 5.2**

### Property 6: Delay warning clearance

*For any* data stream that resumes after a delay, the system SHALL clear the delay warning immediately upon receiving new data.

**Validates: Requirements 5.3**

### Property 7: WebSocket message parsing

*For any* valid JSON message received via WebSocket, the system SHALL successfully parse the message and extract sensor data or motion command fields.

**Validates: Requirements 6.3**

### Property 8: Reconnection behavior

*For any* connection loss event, the system SHALL attempt automatic reconnection with exponential backoff, and SHALL resume data display without user intervention when reconnection succeeds.

**Validates: Requirements 6.4, 6.5**

### Property 9: Pattern change propagation

*For any* motion pattern selection by the user, the system SHALL send the pattern change command to the backend and SHALL display the new pattern name upon successful change.

**Validates: Requirements 8.2, 8.3**

### Property 10: Data grouping

*For any* sensor data display, the system SHALL group acceleration, angular velocity, and angles in separate visual sections.

**Validates: Requirements 7.1**

## Error Handling

### Frontend Error Handling

1. **WebSocket Connection Errors**
   - Connection refused → Display "连接失败" error, show retry button
   - Connection timeout → Display "连接超时" error, attempt auto-reconnect
   - Connection closed unexpectedly → Display "连接断开" warning, attempt auto-reconnect

2. **Data Parsing Errors**
   - Invalid JSON → Log error, skip message, continue listening
   - Missing required fields → Use default values, log warning
   - Invalid data types → Use default values, log warning

3. **Pattern Change Errors**
   - HTTP request failure → Display "模式切换失败" error, retain previous pattern
   - Invalid pattern → Display "无效的运动模式" error

4. **Delay Detection**
   - No data for 2+ seconds → Display "数据延迟" warning
   - Data resumes → Clear warning automatically

### Backend Error Handling

1. **WebSocket Errors**
   - Client disconnect → Clean up resources, stop data generation
   - Send failure → Log error, attempt to continue
   - Data generation error → Send error message to client

2. **Pattern Change Errors**
   - Invalid pattern → Return 400 Bad Request with error message
   - Device not found → Return 404 Not Found

### Error Recovery Strategy

- **Frontend**: Automatic reconnection with exponential backoff (1s, 2s, 4s, 8s, max 30s)
- **Backend**: Graceful degradation, continue serving other clients
- **User notification**: Clear error messages with actionable suggestions

## Testing Strategy

### Manual Testing Approach

由于项目采用手动测试方式，测试将通过以下方法进行：

1. **功能测试**
   - 打开传感器设置界面，验证UI正确渲染
   - 点击"开始订阅"按钮，验证连接建立
   - 观察实时数据更新，验证数值显示正确
   - 验证运动方向显示与后端数据一致
   - 切换运动模式，验证数据特征变化
   - 点击"停止订阅"按钮，验证连接断开

2. **连接测试**
   - 测试WebSocket连接建立和断开
   - 测试自动重连机制（手动断开后端）
   - 测试连接状态指示器显示
   - 测试错误消息显示

3. **数据显示测试**
   - 验证加速度、角速度、角度数值格式（2位小数）
   - 验证运动方向中文标签正确
   - 验证颜色编码正确（绿/红/蓝/灰）
   - 验证运动强度数值显示
   - 验证时间戳显示和更新

4. **延迟检测测试**
   - 暂停后端数据生成，验证2秒后显示延迟警告
   - 恢复数据生成，验证警告自动清除

5. **运动模式测试**
   - 依次测试所有运动模式（forward, backward, turn_left, turn_right, stationary）
   - 验证每种模式的数据特征正确
   - 验证模式切换响应正确

6. **响应式布局测试**
   - 在不同屏幕尺寸下测试界面布局
   - 验证移动端和桌面端显示正常

7. **边界情况测试**
   - 测试极端传感器数值（接近±16g, ±2000°/s, ±180°）
   - 测试快速模式切换
   - 测试长时间运行稳定性

### 测试工具

- **浏览器开发者工具**: 监控WebSocket连接和消息
- **Network面板**: 检查HTTP请求和响应
- **Console面板**: 查看日志和错误信息
- **后端日志**: 验证数据生成和处理

### 测试文档

测试结果将记录在 `SENSOR_DISPLAY_TEST_RESULTS.md` 文件中，包括：
- 测试日期和环境
- 测试场景和步骤
- 预期结果和实际结果
- 发现的问题和解决方案
- 截图和视频记录（如需要）

## Implementation Notes

### WebSocket vs HTTP Polling

- **首选方案**: WebSocket（低延迟，高效）
- **备选方案**: HTTP轮询（兼容性好，但延迟较高）
- **实现策略**: 先尝试WebSocket，失败则降级到HTTP轮询

### Data Update Frequency

- **后端生成频率**: 10Hz (0.1s间隔)
- **前端更新频率**: 实时（收到即更新）
- **UI刷新优化**: 使用React状态批量更新，避免过度渲染

### State Management

- **本地状态**: 使用React useState管理组件状态
- **自定义Hook**: useSensorStream封装WebSocket逻辑
- **状态同步**: 通过回调函数更新父组件状态

### Performance Considerations

1. **避免过度渲染**
   - 使用React.memo优化子组件
   - 合理使用useCallback和useMemo
   - 批量更新状态

2. **WebSocket消息处理**
   - 使用JSON.parse解析消息
   - 验证消息格式后再更新状态
   - 限制消息处理频率（如需要）

3. **内存管理**
   - 组件卸载时清理WebSocket连接
   - 清理定时器和事件监听器
   - 避免内存泄漏

### UI/UX Design

1. **颜色方案**
   - 前进: 绿色 (text-green-500, bg-green-950)
   - 后退: 红色 (text-red-500, bg-red-950)
   - 左转/右转: 蓝色 (text-blue-500, bg-blue-950)
   - 静止: 灰色 (text-slate-500, bg-slate-800)

2. **数据显示**
   - 使用等宽字体 (font-mono) 显示数值
   - 2位小数格式化
   - 清晰的单位标注

3. **状态指示**
   - 连接状态徽章（绿色/灰色/红色）
   - 加载动画（连接中）
   - 错误提示（红色背景）

4. **交互反馈**
   - 按钮悬停效果
   - 点击反馈
   - 平滑过渡动画

### Integration with Existing Code

1. **复用现有组件**
   - 使用现有的UI组件库 (src/components/ui)
   - 保持与现有设计风格一致
   - 复用现有的图标 (lucide-react)

2. **扩展SensorSettings组件**
   - 保留现有的UI结构
   - 替换模拟数据为实时数据
   - 添加连接控制功能

3. **后端集成**
   - 使用现有的MockSensorDevice
   - 使用现有的MotionDirectionProcessor
   - 添加新的API端点

### Configuration

```typescript
// WebSocket配置
const WEBSOCKET_CONFIG = {
  url: 'ws://localhost:8000/api/sensor/stream',
  reconnectInterval: 1000,  // 初始重连间隔（毫秒）
  maxReconnectInterval: 30000,  // 最大重连间隔（毫秒）
  maxReconnectAttempts: 10,  // 最大重连次数
  delayThreshold: 2000,  // 延迟警告阈值（毫秒）
};

// HTTP轮询配置（备选）
const POLLING_CONFIG = {
  url: 'http://localhost:8000/api/sensor/data',
  interval: 100,  // 轮询间隔（毫秒）
};
```

### File Structure

```
src/
├── components/
│   └── settings/
│       └── SensorSettings.tsx  (修改)
├── hooks/
│   └── useSensorStream.ts  (新建)
├── types/
│   └── sensor.ts  (新建)
└── utils/
    └── sensorDataFormatter.ts  (新建)

backend/
└── src/
    └── api/
        └── sensors.py  (新建)
```

