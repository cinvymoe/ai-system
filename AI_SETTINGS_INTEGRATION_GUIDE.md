# AI 识别设置 - 前后端集成指南

## 概述

本指南说明如何测试和使用 AI 识别设置功能，包括前端界面和后端 API 的完整集成。

## 系统架构

```
前端 (React/TypeScript)
  ↓
aiSettingsService.ts (API 客户端)
  ↓
HTTP REST API
  ↓
FastAPI 后端
  ↓
SQLite 数据库 (ai_settings 表)
```

## 数据库表结构

### ai_settings 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| camera_id | STRING | 绑定的摄像头ID |
| camera_name | STRING | 摄像头名称 |
| camera_url | STRING | 摄像头URL |
| confidence_threshold | FLOAT | 置信度阈值 (0-100) |
| danger_zone | JSON | 危险区域4个点 |
| warning_zone | JSON | 警告区域4个点 |
| sound_alarm | BOOLEAN | 声音报警 |
| visual_alarm | BOOLEAN | 视觉报警 |
| auto_screenshot | BOOLEAN | 自动截图 |
| alarm_cooldown | INTEGER | 报警冷却时间(秒) |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

## 启动步骤

### 1. 初始化数据库

```bash
# 创建 AI 设置表并插入默认数据
python backend/init_ai_settings.py
```

输出示例：
```
🔧 初始化 AI 设置数据库表...
✅ 数据库表创建成功
✅ 创建默认 AI 设置 (ID: 1)
   - 置信度阈值: 75.0%
   - 声音报警: True
   - 视觉报警: True
   - 自动截图: True
   - 报警冷却: 5秒
✅ AI 设置初始化完成！
```

### 2. 启动后端服务

```bash
cd backend
python src/main.py
```

后端将在 `http://127.0.0.1:8000` 启动

### 3. 启动前端应用

```bash
npm run dev
```

前端将在 `http://localhost:5173` 启动

## API 端点

### 获取 AI 设置
```http
GET /api/ai-settings
```

### 更新 AI 设置
```http
PUT /api/ai-settings/{settings_id}
Content-Type: application/json

{
  "camera_id": "cam_001",
  "confidence_threshold": 80.0,
  "sound_alarm": true,
  "visual_alarm": true,
  "auto_screenshot": true,
  "alarm_cooldown": 10
}
```

### 绑定摄像头
```http
POST /api/ai-settings/{settings_id}/bind-camera/{camera_id}
```

### 解绑摄像头
```http
POST /api/ai-settings/{settings_id}/unbind-camera
```

## 前端功能

### 1. 绑定识别摄像头
- 下拉选择可用摄像头
- 显示摄像头在线/离线状态
- 显示选中摄像头的详细信息

### 2. 检测参数
- 置信度阈值滑块 (0-100%)
- 实时显示当前值

### 3. 报警设置
- 声音报警开关
- 视觉报警开关
- 自动截图开关
- 报警冷却时间滑块 (0-60秒)

### 4. 保存功能
- 点击"保存设置"按钮
- 显示保存状态（保存中/成功/失败）
- 3秒后自动隐藏提示消息

## 测试步骤

### 1. 测试后端 API

```bash
# 运行测试脚本
python backend/test_ai_settings_api.py
```

测试内容：
- ✅ 获取 AI 设置
- ✅ 更新置信度阈值
- ✅ 设置危险区域
- ✅ 设置警告区域
- ✅ 更新报警设置
- ✅ 绑定摄像头
- ✅ 解绑摄像头

### 2. 测试前端界面

1. **打开 AI 识别设置页面**
   - 导航到设置 → AI识别设置

2. **测试摄像头绑定**
   - 点击摄像头下拉框
   - 选择一个摄像头
   - 查看摄像头详细信息

3. **测试参数调整**
   - 拖动置信度阈值滑块
   - 观察数值变化

4. **测试报警设置**
   - 切换各个开关
   - 调整报警冷却时间

5. **测试保存功能**
   - 修改任意设置
   - 点击"保存设置"
   - 观察保存状态提示
   - 刷新页面验证设置已保存

### 3. 验证数据持久化

```bash
# 查看数据库内容
sqlite3 backend/data/vision_security.db "SELECT * FROM ai_settings;"
```

## 数据流程

### 保存设置流程

```
用户点击保存
  ↓
handleSave() 函数
  ↓
aiSettingsService.updateSettings()
  ↓
PUT /api/ai-settings/{id}
  ↓
AISettingsService.update_settings()
  ↓
AISettingsRepository.update()
  ↓
SQLite 数据库更新
  ↓
返回更新后的设置
  ↓
前端显示成功消息
```

### 加载设置流程

```
组件挂载
  ↓
loadAISettings() 函数
  ↓
aiSettingsService.getSettings()
  ↓
GET /api/ai-settings
  ↓
AISettingsService.get_settings()
  ↓
AISettingsRepository.get_or_create_default()
  ↓
从数据库读取
  ↓
返回设置数据
  ↓
前端更新状态
```

## 常见问题

### 1. 后端连接失败

**问题**: 前端无法连接到后端

**解决方案**:
- 确认后端服务正在运行 (`python backend/src/main.py`)
- 检查端口 8000 是否被占用
- 查看浏览器控制台的网络请求

### 2. 摄像头列表为空

**问题**: 下拉框显示"暂无可用摄像头"

**解决方案**:
- 先添加摄像头（设置 → 摄像头管理）
- 确认摄像头数据已保存到数据库

### 3. 保存失败

**问题**: 点击保存后显示错误

**解决方案**:
- 检查浏览器控制台的错误信息
- 查看后端日志
- 确认数据格式正确

### 4. 设置未持久化

**问题**: 刷新页面后设置丢失

**解决方案**:
- 确认点击了"保存设置"按钮
- 检查数据库文件是否存在
- 查看后端日志确认保存成功

## API 文档

访问 `http://127.0.0.1:8000/docs` 查看完整的 Swagger API 文档

## 文件结构

```
前端:
├── src/services/aiSettingsService.ts    # API 客户端
└── src/components/settings/AISettings.tsx  # UI 组件

后端:
├── backend/src/models/ai_settings.py           # 数据模型
├── backend/src/schemas/ai_settings.py          # 数据验证
├── backend/src/repositories/ai_settings_repository.py  # 数据访问
├── backend/src/services/ai_settings_service.py  # 业务逻辑
├── backend/src/api/ai_settings.py              # API 路由
└── backend/src/database.py                     # 数据库配置

工具:
├── backend/init_ai_settings.py          # 初始化脚本
├── backend/test_ai_settings_api.py      # 测试脚本
└── backend/AI_SETTINGS_API.md           # API 文档
```

## 下一步

1. ✅ 前后端基础集成完成
2. ⏳ 添加危险区域和警告区域的可视化编辑
3. ⏳ 实现 AI 检测功能
4. ⏳ 添加检测历史记录
5. ⏳ 实现实时报警功能

## 总结

AI 识别设置功能已完成前后端集成：

- ✅ 数据库表结构设计
- ✅ 后端 API 实现
- ✅ 前端服务层
- ✅ 前端 UI 组件
- ✅ 数据持久化
- ✅ 摄像头绑定
- ✅ 参数配置
- ✅ 报警设置

用户现在可以通过前端界面配置 AI 识别参数，所有设置都会保存到数据库并在页面刷新后保持。
