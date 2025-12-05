# 摄像头自动监控功能使用指南

## 功能概述

后端现在支持自动定时检测所有已添加摄像头的在线状态，并自动更新数据库中的状态信息。

### 主要特性

- ✅ 自动定时检测（默认每 5 分钟）
- ✅ 后台运行，不影响 API 性能
- ✅ 自动更新摄像头状态到数据库
- ✅ 详细的日志记录
- ✅ 可配置的检测间隔和超时时间
- ✅ 可通过环境变量启用/禁用

## 快速开始

### 1. 安装依赖

```bash
cd backend

# 激活虚拟环境
source .venv/bin/activate

# 安装新依赖
pip install opencv-python apscheduler
# 或使用 uv
uv pip install opencv-python apscheduler
```

### 2. 配置（可选）

复制环境变量示例文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件来自定义配置：

```bash
# 检查间隔（分钟）- 默认 5 分钟
CAMERA_CHECK_INTERVAL_MINUTES=5

# 连接超时（秒）- 默认 5 秒
CAMERA_CHECK_TIMEOUT_SECONDS=5

# 启用自动监控 - 默认 true
ENABLE_AUTO_MONITORING=true

# 日志级别
LOG_LEVEL=INFO
```

### 3. 启动后端

```bash
# 开发模式
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# 或使用 uv
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

启动时会看到类似日志：

```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Camera monitor initialized with 5 minute interval
INFO:     Starting scheduled camera status check...
INFO:     Camera status check #1 completed: 3/4 online, 1 status changed
INFO:     Camera monitor started - checking every 5 minutes
INFO:     Application startup complete.
```

## 手动测试步骤

### 测试 1: 查看监控状态

```bash
curl http://localhost:8000/api/cameras/monitor/status
```

**预期响应：**
```json
{
  "is_running": true,
  "check_interval_minutes": 5,
  "last_check_time": "2024-12-02T10:30:00",
  "total_checks": 3,
  "next_check_time": "2024-12-02T10:35:00"
}
```

### 测试 2: 添加测试摄像头

```bash
# 添加一个在线摄像头（使用真实的 RTSP 地址）
curl -X POST "http://localhost:8000/api/cameras" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "cam-test-001",
    "name": "测试摄像头1",
    "url": "rtsp://192.168.1.100:554/stream",
    "direction": "forward",
    "enabled": true
  }'

# 添加一个离线摄像头（使用无效地址）
curl -X POST "http://localhost:8000/api/cameras" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "cam-test-002",
    "name": "测试摄像头2",
    "url": "rtsp://192.168.1.999:554/stream",
    "direction": "backward",
    "enabled": true
  }'
```

### 测试 3: 手动触发检查

```bash
# 检查所有摄像头
curl -X POST "http://localhost:8000/api/cameras/check-all-status"
```

**预期响应：**
```json
{
  "total_cameras": 2,
  "online_count": 1,
  "offline_count": 1,
  "status_changed_count": 2,
  "cameras": [
    {
      "camera_id": "cam-test-001",
      "camera_name": "测试摄像头1",
      "url": "rtsp://192.168.1.100:554/stream",
      "previous_status": "offline",
      "current_status": "online",
      "is_online": true,
      "status_changed": true
    },
    {
      "camera_id": "cam-test-002",
      "camera_name": "测试摄像头2",
      "url": "rtsp://192.168.1.999:554/stream",
      "previous_status": "offline",
      "current_status": "offline",
      "is_online": false,
      "status_changed": false
    }
  ]
}
```

### 测试 4: 检查单个摄像头

```bash
curl -X POST "http://localhost:8000/api/cameras/cam-test-001/check-status"
```

### 测试 5: 查看摄像头列表

```bash
curl http://localhost:8000/api/cameras
```

验证 `status` 字段已更新为 `online` 或 `offline`。

### 测试 6: 观察自动检测

等待 5 分钟（或你配置的间隔时间），观察后端日志：

```
INFO:     Starting scheduled camera status check...
INFO:     Camera status check #2 completed: 1/2 online, 0 status changed
WARNING:  Camera offline: 测试摄像头2 (cam-test-002) - rtsp://192.168.1.999:554/stream
```

### 测试 7: 验证状态持久化

重启后端服务，检查摄像头状态是否保持：

```bash
# 停止服务 (Ctrl+C)
# 重新启动
uvicorn src.main:app --reload

# 查看摄像头列表
curl http://localhost:8000/api/cameras
```

## 配置选项

### 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `CAMERA_CHECK_INTERVAL_MINUTES` | 5 | 自动检查间隔（分钟） |
| `CAMERA_CHECK_TIMEOUT_SECONDS` | 5 | 连接超时时间（秒） |
| `ENABLE_AUTO_MONITORING` | true | 是否启用自动监控 |
| `LOG_LEVEL` | INFO | 日志级别 |

### 修改检查间隔

**方法 1: 环境变量**
```bash
export CAMERA_CHECK_INTERVAL_MINUTES=10
uvicorn src.main:app --reload
```

**方法 2: .env 文件**
```bash
echo "CAMERA_CHECK_INTERVAL_MINUTES=10" >> .env
uvicorn src.main:app --reload
```

### 禁用自动监控

```bash
export ENABLE_AUTO_MONITORING=false
uvicorn src.main:app --reload
```

或在 `.env` 文件中：
```
ENABLE_AUTO_MONITORING=false
```

## 日志说明

### 正常运行日志

```
INFO: Camera monitor initialized with 5 minute interval
INFO: Starting scheduled camera status check...
INFO: Checking camera online status: rtsp://192.168.1.100:554/stream
INFO: Camera online: rtsp://192.168.1.100:554/stream
INFO: Camera status check #1 completed: 3/4 online, 1 status changed
INFO: Camera monitor started - checking every 5 minutes
```

### 离线摄像头警告

```
WARNING: Camera offline: Failed to open stream rtsp://192.168.1.999:554/stream
WARNING: Camera offline: 测试摄像头 (cam-001) - rtsp://192.168.1.999:554/stream
```

### 错误日志

```
ERROR: Error checking camera status for rtsp://invalid: Connection timeout
ERROR: Error during scheduled camera status check: Database connection failed
```

## API 端点

### 查看监控状态

```
GET /api/cameras/monitor/status
```

返回监控服务的当前状态。

### 手动检查所有摄像头

```
POST /api/cameras/check-all-status
```

立即检查所有摄像头状态（不等待定时任务）。

### 手动检查单个摄像头

```
POST /api/cameras/{camera_id}/check-status
```

立即检查指定摄像头状态。

## 性能考虑

### 检查间隔建议

- **少量摄像头（1-10）**: 3-5 分钟
- **中等数量（10-50）**: 5-10 分钟
- **大量摄像头（50+）**: 10-15 分钟

### 超时时间建议

- **本地网络**: 3-5 秒
- **远程网络**: 5-10 秒
- **不稳定网络**: 10-15 秒

### 资源使用

- 每次检查会为每个摄像头创建一个短暂的连接
- 内存占用：约 50-100MB（取决于摄像头数量）
- CPU 使用：检查期间会有短暂峰值

## 故障排除

### 问题 1: 监控未启动

**症状：** 日志中没有 "Camera monitor started" 消息

**解决方案：**
1. 检查 `ENABLE_AUTO_MONITORING` 是否为 `true`
2. 查看启动日志是否有错误
3. 确认 apscheduler 已安装

### 问题 2: 所有摄像头显示离线

**症状：** 所有摄像头 `status` 都是 `offline`

**解决方案：**
1. 检查摄像头 URL 是否正确
2. 确认网络连接正常
3. 增加超时时间：`CAMERA_CHECK_TIMEOUT_SECONDS=10`
4. 手动测试摄像头连接

### 问题 3: 检查太频繁或太慢

**解决方案：**
调整 `CAMERA_CHECK_INTERVAL_MINUTES` 环境变量。

### 问题 4: OpenCV 连接失败

**症状：** 日志显示 "Failed to open stream"

**解决方案：**
1. 确认 opencv-python 已正确安装
2. 测试摄像头 URL 是否可访问
3. 检查防火墙设置
4. 验证 RTSP 协议支持

## 生产环境建议

1. **使用环境变量配置**
   ```bash
   export CAMERA_CHECK_INTERVAL_MINUTES=10
   export CAMERA_CHECK_TIMEOUT_SECONDS=8
   export LOG_LEVEL=WARNING
   ```

2. **设置合理的检查间隔**
   - 避免过于频繁的检查
   - 根据摄像头数量调整

3. **监控日志**
   - 定期检查离线摄像头警告
   - 关注错误日志

4. **数据库备份**
   - 定期备份摄像头配置
   - 保存状态历史记录

5. **使用进程管理器**
   ```bash
   # 使用 systemd 或 supervisor 管理服务
   # 确保服务自动重启
   ```

## 下一步

- [ ] 添加状态变化通知（邮件/webhook）
- [ ] 记录状态历史到数据库
- [ ] 添加监控仪表板
- [ ] 支持批量操作
- [ ] 添加健康检查 API
