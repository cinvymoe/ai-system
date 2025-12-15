# RTSP 播放模块使用说明

## 概述

RTSP 播放模块通过 WebSocket 实时传输 RTSP 视频流，支持多路流同时播放。

## 快速开始

### 1. 启动 RTSP 流

```bash
curl -X POST http://127.0.0.1:8000/rtsp/streams/start \
  -H "Content-Type: application/json" \
  -d '{
    "stream_id": "camera1",
    "rtsp_url": "rtsp://admin:password@192.168.1.100:554/stream1"
  }'
```

**响应示例：**
```json
{
  "success": true,
  "message": "Stream camera1 started successfully",
  "stream_id": "camera1"
}
```

### 2. 通过 WebSocket 接收视频流

**JavaScript 示例：**
```javascript
const ws = new WebSocket('ws://127.0.0.1:8000/rtsp/ws/camera1');

ws.onopen = () => {
  console.log('WebSocket 已连接');
};

ws.onmessage = (event) => {
  if (event.data instanceof Blob) {
    // 接收到 JPEG 图像帧
    const url = URL.createObjectURL(event.data);
    document.getElementById('video').src = url;
  } else {
    // 接收到 JSON 消息
    const msg = JSON.parse(event.data);
    console.log('消息:', msg);
  }
};
```

### 3. 查看所有活动流

```bash
curl http://127.0.0.1:8000/rtsp/streams
```

**响应示例：**
```json
{
  "streams": [
    {
      "stream_id": "camera1",
      "width": 1920,
      "height": 1080,
      "fps": 25,
      "is_opened": true,
      "connections": 2
    }
  ],
  "total": 1
}
```

### 4. 查看单个流信息

```bash
curl http://127.0.0.1:8000/rtsp/streams/camera1
```

### 5. 停止 RTSP 流

```bash
curl -X POST http://127.0.0.1:8000/rtsp/streams/stop/camera1
```

## 完整的 HTML 测试页面

创建 `test_rtsp.html`：

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>RTSP 流测试</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            padding: 20px; 
            background: #1e293b;
            color: #e2e8f0;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { color: #22d3ee; }
        .controls { 
            background: #0f172a; 
            padding: 20px; 
            border-radius: 8px; 
            margin-bottom: 20px;
        }
        input, button { 
            padding: 10px; 
            margin: 5px; 
            border-radius: 5px;
            border: 1px solid #334155;
        }
        input { 
            width: 400px; 
            background: #1e293b;
            color: #e2e8f0;
        }
        button { 
            background: #3b82f6; 
            color: white; 
            cursor: pointer;
            border: none;
        }
        button:hover { background: #2563eb; }
        #video { 
            max-width: 100%; 
            border: 2px solid #334155;
            border-radius: 8px;
        }
        .status { 
            padding: 10px; 
            margin: 10px 0;
            border-radius: 5px;
            background: #0f172a;
        }
        .success { color: #22c55e; }
        .error { color: #ef4444; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📹 RTSP 流播放器</h1>
        
        <div class="controls">
            <h3>流控制</h3>
            <div>
                <input type="text" id="streamId" placeholder="流 ID (例如: camera1)" value="camera1">
                <input type="text" id="rtspUrl" placeholder="RTSP URL" 
                       value="rtsp://admin:password@192.168.1.100:554/stream1">
            </div>
            <div>
                <button onclick="startStream()">▶️ 启动流</button>
                <button onclick="connectWebSocket()">🔗 连接 WebSocket</button>
                <button onclick="stopStream()">⏹️ 停止流</button>
                <button onclick="listStreams()">📋 列出所有流</button>
            </div>
            <div id="status" class="status"></div>
        </div>
        
        <div>
            <h3>视频预览</h3>
            <img id="video" alt="等待视频流..." style="background: #0f172a;">
        </div>
        
        <div class="controls">
            <h3>统计信息</h3>
            <div id="stats">
                <p>帧数: <span id="frameCount">0</span></p>
                <p>FPS: <span id="fps">0</span></p>
                <p>连接状态: <span id="wsStatus">未连接</span></p>
            </div>
        </div>
    </div>

    <script>
        let ws = null;
        let frameCount = 0;
        let lastFrameTime = Date.now();
        let fpsCounter = 0;
        
        const API_BASE = 'http://127.0.0.1:8000/rtsp';
        const WS_BASE = 'ws://127.0.0.1:8000/rtsp';

        function log(message, isError = false) {
            const status = document.getElementById('status');
            status.innerHTML = `<span class="${isError ? 'error' : 'success'}">${message}</span>`;
            console.log(message);
        }

        async function startStream() {
            const streamId = document.getElementById('streamId').value;
            const rtspUrl = document.getElementById('rtspUrl').value;
            
            if (!streamId || !rtspUrl) {
                log('请填写流 ID 和 RTSP URL', true);
                return;
            }
            
            try {
                const response = await fetch(`${API_BASE}/streams/start`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ stream_id: streamId, rtsp_url: rtspUrl })
                });
                
                const data = await response.json();
                if (response.ok) {
                    log(`✓ 流 ${streamId} 启动成功`);
                } else {
                    log(`✗ 启动失败: ${data.detail}`, true);
                }
            } catch (error) {
                log(`✗ 请求失败: ${error.message}`, true);
            }
        }

        function connectWebSocket() {
            const streamId = document.getElementById('streamId').value;
            
            if (!streamId) {
                log('请填写流 ID', true);
                return;
            }
            
            if (ws) {
                ws.close();
            }
            
            ws = new WebSocket(`${WS_BASE}/ws/${streamId}`);
            document.getElementById('wsStatus').textContent = '连接中...';
            
            ws.onopen = () => {
                log(`✓ WebSocket 已连接到流 ${streamId}`);
                document.getElementById('wsStatus').textContent = '已连接';
                frameCount = 0;
                fpsCounter = 0;
            };
            
            ws.onmessage = (event) => {
                if (event.data instanceof Blob) {
                    // 接收到图像帧
                    const url = URL.createObjectURL(event.data);
                    const img = document.getElementById('video');
                    
                    // 释放旧的 URL
                    if (img.src.startsWith('blob:')) {
                        URL.revokeObjectURL(img.src);
                    }
                    
                    img.src = url;
                    
                    // 更新统计
                    frameCount++;
                    fpsCounter++;
                    document.getElementById('frameCount').textContent = frameCount;
                    
                    // 计算 FPS
                    const now = Date.now();
                    if (now - lastFrameTime >= 1000) {
                        document.getElementById('fps').textContent = fpsCounter;
                        fpsCounter = 0;
                        lastFrameTime = now;
                    }
                } else {
                    // JSON 消息
                    const msg = JSON.parse(event.data);
                    if (msg.type === 'error') {
                        log(`✗ ${msg.message}`, true);
                    } else if (msg.type === 'connected') {
                        log(`✓ ${msg.message}`);
                    }
                }
            };
            
            ws.onerror = () => {
                log('✗ WebSocket 连接错误', true);
                document.getElementById('wsStatus').textContent = '错误';
            };
            
            ws.onclose = () => {
                log('WebSocket 已断开');
                document.getElementById('wsStatus').textContent = '已断开';
            };
        }

        async function stopStream() {
            const streamId = document.getElementById('streamId').value;
            
            if (!streamId) {
                log('请填写流 ID', true);
                return;
            }
            
            if (ws) {
                ws.close();
                ws = null;
            }
            
            try {
                const response = await fetch(`${API_BASE}/streams/stop/${streamId}`, {
                    method: 'POST'
                });
                
                const data = await response.json();
                if (response.ok) {
                    log(`✓ 流 ${streamId} 已停止`);
                } else {
                    log(`✗ 停止失败: ${data.detail}`, true);
                }
            } catch (error) {
                log(`✗ 请求失败: ${error.message}`, true);
            }
        }

        async function listStreams() {
            try {
                const response = await fetch(`${API_BASE}/streams`);
                const data = await response.json();
                
                if (response.ok) {
                    log(`✓ 当前活动流: ${data.total} 个`);
                    console.log('流列表:', data.streams);
                } else {
                    log('✗ 获取流列表失败', true);
                }
            } catch (error) {
                log(`✗ 请求失败: ${error.message}`, true);
            }
        }
    </script>
</body>
</html>
```

## Python 测试脚本

创建 `test_rtsp_client.py`：

```python
import asyncio
import websockets
from PIL import Image
from io import BytesIO

async def test_rtsp_stream():
    uri = "ws://127.0.0.1:8000/rtsp/ws/camera1"
    
    async with websockets.connect(uri) as websocket:
        print("WebSocket 已连接")
        
        frame_count = 0
        while True:
            message = await websocket.recv()
            
            if isinstance(message, bytes):
                # 接收到图像帧
                frame_count += 1
                print(f"接收到第 {frame_count} 帧")
                
                # 可选：保存或显示图像
                # image = Image.open(BytesIO(message))
                # image.save(f"frame_{frame_count}.jpg")
            else:
                # JSON 消息
                print(f"消息: {message}")

if __name__ == "__main__":
    asyncio.run(test_rtsp_stream())
```

## API 端点

### POST /rtsp/streams/start
启动 RTSP 流

**请求体：**
```json
{
  "stream_id": "camera1",
  "rtsp_url": "rtsp://..."
}
```

### POST /rtsp/streams/stop/{stream_id}
停止指定流

### GET /rtsp/streams
列出所有活动流

### GET /rtsp/streams/{stream_id}
获取指定流信息

### WebSocket /rtsp/ws/{stream_id}
连接到视频流，接收 JPEG 帧

## 常见 RTSP URL 格式

```bash
# 海康威信
rtsp://admin:password@192.168.1.100:554/Streaming/Channels/101

# 大华
rtsp://admin:password@192.168.1.100:554/cam/realmonitor?channel=1&subtype=0

# 通用格式
rtsp://username:password@ip:port/path
```

## 注意事项

1. **性能**：每个流会占用一定的 CPU 和内存资源
2. **网络**：确保服务器能访问 RTSP 源
3. **编码**：视频帧以 JPEG 格式传输，质量设置为 80%
4. **帧率**：WebSocket 默认约 30 FPS，可在代码中调整
5. **并发**：支持多个客户端同时连接同一个流

## 故障排查

**问题：无法连接 RTSP 源**
- 检查 RTSP URL 是否正确
- 确认网络连通性
- 验证用户名密码

**问题：WebSocket 连接失败**
- 确保先启动流（POST /streams/start）
- 检查 stream_id 是否正确
- 查看后端日志

**问题：视频卡顿**
- 检查网络带宽
- 降低 JPEG 质量（修改 rtsp_service.py 中的质量参数）
- 减少帧率
