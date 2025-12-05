# AI 识别设置 API 文档

## 概述

AI 识别设置 API 提供了管理 AI 识别配置的接口，包括摄像头绑定、检测参数、危险区域设置和报警配置。

## 数据库表结构

### ai_settings 表

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INTEGER | 主键，自增 |
| camera_id | STRING | 绑定的摄像头ID |
| camera_name | STRING | 摄像头名称（冗余字段） |
| camera_url | STRING | 摄像头URL（冗余字段） |
| confidence_threshold | FLOAT | 置信度阈值 (0-100) |
| danger_zone | JSON | 危险区域的4个点坐标 |
| warning_zone | JSON | 警告区域的4个点坐标 |
| sound_alarm | BOOLEAN | 是否启用声音报警 |
| visual_alarm | BOOLEAN | 是否启用视觉报警 |
| auto_screenshot | BOOLEAN | 是否自动截图 |
| alarm_cooldown | INTEGER | 报警冷却时间（秒） |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### 区域坐标格式

危险区域和警告区域都使用4个点的坐标数组，坐标值为相对坐标 (0-1)：

```json
[
  {"x": 0.1, "y": 0.2},
  {"x": 0.4, "y": 0.2},
  {"x": 0.4, "y": 0.8},
  {"x": 0.1, "y": 0.8}
]
```

## API 端点

### 1. 获取 AI 设置

```http
GET /api/ai-settings
```

**响应示例：**

```json
{
  "id": 1,
  "camera_id": "cam_001",
  "camera_name": "前方摄像头",
  "camera_url": "rtsp://192.168.1.100:554/stream",
  "confidence_threshold": 75.0,
  "danger_zone": [
    {"x": 0.1, "y": 0.2},
    {"x": 0.4, "y": 0.2},
    {"x": 0.4, "y": 0.8},
    {"x": 0.1, "y": 0.8}
  ],
  "warning_zone": [
    {"x": 0.5, "y": 0.3},
    {"x": 0.8, "y": 0.3},
    {"x": 0.8, "y": 0.7},
    {"x": 0.5, "y": 0.7}
  ],
  "sound_alarm": true,
  "visual_alarm": true,
  "auto_screenshot": true,
  "alarm_cooldown": 5,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

### 2. 创建 AI 设置

```http
POST /api/ai-settings
Content-Type: application/json
```

**请求体：**

```json
{
  "camera_id": "cam_001",
  "confidence_threshold": 75.0,
  "danger_zone": [
    {"x": 0.1, "y": 0.2},
    {"x": 0.4, "y": 0.2},
    {"x": 0.4, "y": 0.8},
    {"x": 0.1, "y": 0.8}
  ],
  "warning_zone": [
    {"x": 0.5, "y": 0.3},
    {"x": 0.8, "y": 0.3},
    {"x": 0.8, "y": 0.7},
    {"x": 0.5, "y": 0.7}
  ],
  "sound_alarm": true,
  "visual_alarm": true,
  "auto_screenshot": true,
  "alarm_cooldown": 5
}
```

### 3. 更新 AI 设置

```http
PUT /api/ai-settings/{settings_id}
Content-Type: application/json
```

**请求体（所有字段可选）：**

```json
{
  "confidence_threshold": 80.0,
  "sound_alarm": false,
  "alarm_cooldown": 10
}
```

### 4. 删除 AI 设置

```http
DELETE /api/ai-settings/{settings_id}
```

### 5. 绑定摄像头

```http
POST /api/ai-settings/{settings_id}/bind-camera/{camera_id}
```

自动更新 `camera_name` 和 `camera_url` 字段。

### 6. 解绑摄像头

```http
POST /api/ai-settings/{settings_id}/unbind-camera
```

将 `camera_id`、`camera_name` 和 `camera_url` 设置为 null。

## 初始化

### 1. 初始化数据库表

```bash
cd backend
python init_ai_settings.py
```

这将创建 `ai_settings` 表并插入默认设置。

### 2. 启动后端服务

```bash
cd backend
python src/main.py
```

服务将在 `http://127.0.0.1:8000` 启动。

## 测试

### 运行测试脚本

```bash
cd backend
python test_ai_settings_api.py
```

测试脚本将执行以下操作：
1. 获取 AI 设置
2. 更新置信度阈值
3. 设置危险区域
4. 设置警告区域
5. 更新报警设置
6. 绑定摄像头
7. 解绑摄像头
8. 获取最终设置

### 使用 Swagger UI

访问 `http://127.0.0.1:8000/docs` 查看交互式 API 文档。

## 前端集成

### TypeScript 接口定义

```typescript
interface Point {
  x: number; // 0-1
  y: number; // 0-1
}

interface AISettings {
  id: number;
  camera_id: string | null;
  camera_name: string | null;
  camera_url: string | null;
  confidence_threshold: number; // 0-100
  danger_zone: Point[] | null; // 4个点
  warning_zone: Point[] | null; // 4个点
  sound_alarm: boolean;
  visual_alarm: boolean;
  auto_screenshot: boolean;
  alarm_cooldown: number; // 秒
  created_at: string;
  updated_at: string;
}
```

### 示例：获取设置

```typescript
async function getAISettings(): Promise<AISettings> {
  const response = await fetch('http://127.0.0.1:8000/api/ai-settings');
  if (!response.ok) {
    throw new Error('Failed to fetch AI settings');
  }
  return await response.json();
}
```

### 示例：更新设置

```typescript
async function updateAISettings(
  settingsId: number,
  updates: Partial<AISettings>
): Promise<AISettings> {
  const response = await fetch(
    `http://127.0.0.1:8000/api/ai-settings/${settingsId}`,
    {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(updates),
    }
  );
  if (!response.ok) {
    throw new Error('Failed to update AI settings');
  }
  return await response.json();
}
```

### 示例：绑定摄像头

```typescript
async function bindCamera(
  settingsId: number,
  cameraId: string
): Promise<AISettings> {
  const response = await fetch(
    `http://127.0.0.1:8000/api/ai-settings/${settingsId}/bind-camera/${cameraId}`,
    {
      method: 'POST',
    }
  );
  if (!response.ok) {
    throw new Error('Failed to bind camera');
  }
  return await response.json();
}
```

## 注意事项

1. **区域坐标验证**：危险区域和警告区域必须包含恰好4个点
2. **摄像头验证**：绑定摄像头时会验证摄像头是否存在
3. **自动填充**：绑定摄像头时会自动填充 `camera_name` 和 `camera_url`
4. **默认设置**：首次调用 GET 接口时会自动创建默认设置
5. **置信度范围**：置信度阈值必须在 0-100 之间
6. **冷却时间**：报警冷却时间必须 >= 0

## 错误处理

### 常见错误

| 状态码 | 错误信息 | 说明 |
|--------|----------|------|
| 400 | 危险区域必须包含4个点 | 区域点数量不正确 |
| 400 | 摄像头 xxx 不存在 | 尝试绑定不存在的摄像头 |
| 404 | AI设置不存在 | 指定的设置ID不存在 |

### 错误响应示例

```json
{
  "detail": "危险区域必须包含4个点"
}
```
