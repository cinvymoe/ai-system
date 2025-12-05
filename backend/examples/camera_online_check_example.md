# 摄像头在线检查功能使用示例

## 功能概述

后端提供了三个新的 API 端点来检查摄像头是否在线：

1. **检查单个摄像头状态** - `POST /api/cameras/{camera_id}/check-status`
2. **检查所有摄像头状态** - `POST /api/cameras/check-all-status`
3. **手动更新摄像头状态** - `PATCH /api/cameras/{camera_id}/status`

## API 使用示例

### 1. 检查单个摄像头是否在线

```bash
curl -X POST "http://localhost:8000/api/cameras/cam-001/check-status"
```

**响应示例：**
```json
{
  "camera_id": "cam-001",
  "camera_name": "前方摄像头",
  "url": "rtsp://192.168.1.100:554/stream",
  "previous_status": "offline",
  "current_status": "online",
  "is_online": true,
  "status_changed": true
}
```

### 2. 检查所有摄像头状态

```bash
curl -X POST "http://localhost:8000/api/cameras/check-all-status"
```

**响应示例：**
```json
{
  "total_cameras": 4,
  "online_count": 3,
  "offline_count": 1,
  "status_changed_count": 2,
  "cameras": [
    {
      "camera_id": "cam-001",
      "camera_name": "前方摄像头",
      "url": "rtsp://192.168.1.100:554/stream",
      "previous_status": "offline",
      "current_status": "online",
      "is_online": true,
      "status_changed": true
    },
    {
      "camera_id": "cam-002",
      "camera_name": "后方摄像头",
      "url": "rtsp://192.168.1.101:554/stream",
      "previous_status": "online",
      "current_status": "online",
      "is_online": true,
      "status_changed": false
    }
  ]
}
```

### 3. 手动更新摄像头状态

```bash
curl -X PATCH "http://localhost:8000/api/cameras/cam-001/status?status=online"
```

## Python 代码示例

### 使用 requests 库

```python
import requests

BASE_URL = "http://localhost:8000"

# 检查单个摄像头
def check_camera_status(camera_id: str):
    response = requests.post(f"{BASE_URL}/api/cameras/{camera_id}/check-status")
    if response.status_code == 200:
        data = response.json()
        print(f"摄像头 {data['camera_name']} 状态: {data['current_status']}")
        print(f"在线: {data['is_online']}")
        return data
    else:
        print(f"错误: {response.status_code}")
        return None

# 检查所有摄像头
def check_all_cameras():
    response = requests.post(f"{BASE_URL}/api/cameras/check-all-status")
    if response.status_code == 200:
        data = response.json()
        print(f"总摄像头数: {data['total_cameras']}")
        print(f"在线: {data['online_count']}, 离线: {data['offline_count']}")
        
        for camera in data['cameras']:
            status_icon = "✓" if camera['is_online'] else "✗"
            print(f"{status_icon} {camera['camera_name']}: {camera['current_status']}")
        
        return data
    else:
        print(f"错误: {response.status_code}")
        return None

# 使用示例
if __name__ == "__main__":
    # 检查单个摄像头
    check_camera_status("cam-001")
    
    # 检查所有摄像头
    check_all_cameras()
```

## 工作原理

### 在线检查逻辑

1. 使用 OpenCV 的 `VideoCapture` 尝试连接摄像头流
2. 设置连接超时时间（默认 5 秒）
3. 检查流是否成功打开
4. 尝试读取一帧数据验证流是否正常工作
5. 根据结果返回在线/离线状态

### 支持的协议

- RTSP (rtsp://)
- HTTP/HTTPS (http://, https://)
- 本地摄像头 (0, 1, 2, ...)
- 文件路径

### 超时设置

默认连接超时为 5 秒，可以在调用时自定义：

```python
# 在 camera_service.py 中
is_online = camera_service.check_camera_online(camera_url, timeout=10)
```

## 定时任务集成

可以使用定时任务定期检查所有摄像头状态：

```python
import schedule
import time
import requests

def check_cameras_job():
    """定时检查所有摄像头状态"""
    response = requests.post("http://localhost:8000/api/cameras/check-all-status")
    if response.status_code == 200:
        data = response.json()
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] "
              f"在线: {data['online_count']}/{data['total_cameras']}")

# 每 5 分钟检查一次
schedule.every(5).minutes.do(check_cameras_job)

while True:
    schedule.run_pending()
    time.sleep(1)
```

## 错误处理

API 会返回以下错误码：

- **404**: 摄像头不存在
- **500**: 服务器内部错误（数据库错误、连接失败等）

错误响应示例：
```json
{
  "detail": "Camera with ID 'cam-999' not found"
}
```

## 性能考虑

- 每次检查需要建立网络连接，可能需要几秒钟
- 检查所有摄像头时是串行执行的
- 建议不要过于频繁地调用（建议间隔至少 1-5 分钟）
- 对于大量摄像头，考虑使用异步或后台任务

## 日志

所有检查操作都会记录日志：

```
INFO: Checking camera online status: rtsp://192.168.1.100:554/stream
INFO: Camera online: rtsp://192.168.1.100:554/stream
INFO: Camera cam-001 status changed: offline -> online
```
