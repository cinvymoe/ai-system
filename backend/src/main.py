# -*- coding: utf-8 -*-
"""Main entry point for the vision security backend."""

import sys
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Add parent directory to path for datahandler module
parent_dir = Path(__file__).parent.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager

try:
    from database import init_db, get_db
except ImportError:
    from src.database import init_db, get_db

try:
    from api.cameras import router as cameras_router
    from api.angle_ranges import router as angle_ranges_router
    from api.sensors import router as sensors_router
    from api.ai_settings import router as ai_settings_router
    from api.broker import router as broker_router
    from api.rtsp import router as rtsp_router
    from api.person_detection import router as person_detection_router
except ImportError:
    from src.api.cameras import router as cameras_router
    from src.api.angle_ranges import router as angle_ranges_router
    from src.api.sensors import router as sensors_router
    from src.api.ai_settings import router as ai_settings_router
    from src.api.broker import router as broker_router
    from src.api.rtsp import router as rtsp_router
    from src.api.person_detection import router as person_detection_router

try:
    from scheduler.camera_monitor import get_camera_monitor
    from scheduler.person_detector import get_person_detection_monitor
except ImportError:
    from src.scheduler.camera_monitor import get_camera_monitor
    from src.scheduler.person_detector import get_person_detection_monitor

try:
    from config import settings
except ImportError:
    from src.config import settings

try:
    from broker import configure_broker_logging
    from broker.broker import MessageBroker
    from broker.handlers import DirectionMessageHandler, AngleMessageHandler, AIAlertMessageHandler
    from broker.mapper import CameraMapper
except ImportError:
    from src.broker import configure_broker_logging
    from src.broker.broker import MessageBroker
    from src.broker.handlers import DirectionMessageHandler, AngleMessageHandler, AIAlertMessageHandler
    from src.broker.mapper import CameraMapper


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager.
    
    Handles startup and shutdown events for the FastAPI application.
    On startup, initializes the database, message broker, and starts camera monitoring.
    On shutdown, stops the camera monitor and shuts down the message broker.
    """
    # Configure broker logging
    configure_broker_logging(
        log_level=settings.LOG_LEVEL,
        use_structured=False,  # Can be made configurable via env var
        log_file=None  # Can be made configurable via env var
    )
    
    # Suppress APScheduler job execution logs
    logging.getLogger('apscheduler.executors.default').setLevel(logging.WARNING)
    
    # Startup: Initialize database
    init_db()
    
    # Initialize message broker with handlers and camera mapper
    broker = MessageBroker.get_instance()
    camera_mapper = CameraMapper(db_session_factory=get_db)
    broker.initialize_handlers(camera_mapper)
    
    # Start camera monitoring if enabled
    if settings.ENABLE_AUTO_MONITORING:
        monitor = get_camera_monitor(check_interval_minutes=settings.CAMERA_CHECK_INTERVAL_MINUTES)
        monitor.start()
    
    # Start person detection monitor if model path is configured
    person_detection_model = settings.PERSON_DETECTION_MODEL_PATH
    person_detection_interval = int(os.getenv('PERSON_DETECTION_INTERVAL_SECONDS', '1'))
    
    if person_detection_model :
        try:
            detection_monitor = get_person_detection_monitor(
                model_path=person_detection_model,
                check_interval_seconds=person_detection_interval
            )
            detection_monitor.start()
            logger.info(f"Person detection monitor started with model: {person_detection_model}")
        except Exception as e:
            logger.error(f"Failed to start person detection monitor: {e}")
    else:
        logger.info("Person detection monitor not started (model path not configured or not found)")
    
    yield
    
    # Shutdown: Stop camera monitor if it was started
    if settings.ENABLE_AUTO_MONITORING:
        monitor = get_camera_monitor()
        monitor.stop()
    
    # Shutdown: Stop person detection monitor if it was started
    try:
        from src.scheduler.person_detector import _detection_monitor_instance
        if _detection_monitor_instance is not None:
            _detection_monitor_instance.stop()
            logger.info("Person detection monitor stopped")
    except Exception as e:
        logger.error(f"Error stopping person detection monitor: {e}")
    
    # Shutdown message broker
    broker.shutdown()


app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    lifespan=lifespan
)

# Include API routes
app.include_router(cameras_router)
app.include_router(angle_ranges_router)
app.include_router(sensors_router)
app.include_router(ai_settings_router)
app.include_router(broker_router)
app.include_router(rtsp_router)
app.include_router(person_detection_router)

# Add CORS middleware to support frontend cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint - Hello World."""
    return {"message": "Hello World", "service": "Vision Security Backend"}


@app.get("/test", response_class=HTMLResponse)
async def test_index():
    """测试页面索引"""
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>测试页面索引</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            padding: 40px; 
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            color: #e2e8f0;
            min-height: 100vh;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: #1e293b;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
        }
        h1 { 
            color: #22d3ee; 
            margin-bottom: 30px;
            text-align: center;
        }
        .test-list {
            list-style: none;
            padding: 0;
        }
        .test-item {
            background: #0f172a;
            margin: 15px 0;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #3b82f6;
            transition: all 0.3s ease;
        }
        .test-item:hover {
            transform: translateX(5px);
            border-left-color: #22d3ee;
            box-shadow: 0 4px 8px rgba(34, 211, 238, 0.2);
        }
        .test-item h3 {
            color: #22d3ee;
            margin: 0 0 10px 0;
        }
        .test-item p {
            color: #94a3b8;
            margin: 0 0 15px 0;
        }
        .test-item a {
            display: inline-block;
            padding: 10px 20px;
            background: #3b82f6;
            color: white;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 600;
            transition: all 0.2s ease;
        }
        .test-item a:hover {
            background: #2563eb;
            transform: translateY(-2px);
        }
        .info-box {
            background: #0f172a;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            border: 1px solid #334155;
        }
        .info-box h2 {
            color: #22d3ee;
            margin-top: 0;
        }
        .status {
            display: inline-block;
            padding: 5px 12px;
            background: #22c55e;
            color: #000;
            border-radius: 4px;
            font-weight: bold;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🧪 Vision Security Backend - 测试页面</h1>
        
        <div class="info-box">
            <h2>服务状态</h2>
            <p><span class="status">✓ 运行中</span></p>
            <p style="color: #94a3b8; margin-top: 10px;">
                Backend API: <code style="color: #22d3ee;">http://127.0.0.1:8000</code><br>
                WebSocket: <code style="color: #22d3ee;">ws://127.0.0.1:8000/api/sensor/stream</code>
            </p>
        </div>
        
        <ul class="test-list">
            <li class="test-item">
                <h3>🔌 WebSocket 连接测试</h3>
                <p>实时测试 WebSocket 连接，查看传感器数据流和运动指令</p>
                <a href="/test/websocket" target="_blank">打开测试页面 →</a>
            </li>
            
            <li class="test-item">
                <h3>📡 消息代理 WebSocket 测试</h3>
                <p>测试消息代理的 WebSocket 连接，查看摄像头列表更新</p>
                <a href="/test/broker-websocket" target="_blank">打开代理测试页面 →</a>
            </li>
            
            <li class="test-item">
                <h3>📡 API 健康检查</h3>
                <p>检查后端 API 服务是否正常运行</p>
                <a href="/health" target="_blank">查看健康状态 →</a>
            </li>
            
            <li class="test-item">
                <h3>📚 API 文档</h3>
                <p>查看完整的 API 接口文档（Swagger UI）</p>
                <a href="/docs" target="_blank">打开 API 文档 →</a>
            </li>
            
            <li class="test-item">
                <h3>🔄 ReDoc 文档</h3>
                <p>另一种风格的 API 文档界面</p>
                <a href="/redoc" target="_blank">打开 ReDoc →</a>
            </li>
        </ul>
    </div>
</body>
</html>
    """
    return HTMLResponse(content=html_content)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/test/broker-websocket", response_class=HTMLResponse)
async def broker_websocket_test_page():
    """消息代理 WebSocket 测试页面"""
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>消息代理 WebSocket 测试页面</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            padding: 20px; 
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            color: #e2e8f0;
            min-height: 100vh;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        h1 { 
            color: #22d3ee; 
            margin-bottom: 30px;
            font-size: 2em;
            text-align: center;
        }
        .status-card {
            background: #1e293b;
            border: 2px solid #334155;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }
        .status { 
            padding: 15px 25px; 
            border-radius: 8px; 
            font-size: 18px;
            font-weight: bold;
            text-align: center;
            margin-bottom: 20px;
            transition: all 0.3s ease;
        }
        .connecting { background: #fbbf24; color: #000; }
        .connected { background: #22c55e; color: #000; }
        .disconnected { background: #64748b; color: #fff; }
        .error { background: #ef4444; color: #fff; }
        
        .button-group {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-bottom: 20px;
        }
        button { 
            padding: 12px 24px; 
            font-size: 16px;
            cursor: pointer; 
            border-radius: 8px;
            border: none;
            background: #3b82f6;
            color: white;
            font-weight: 600;
            transition: all 0.2s ease;
            flex: 1;
            min-width: 150px;
        }
        button:hover { 
            background: #2563eb; 
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(59, 130, 246, 0.4);
        }
        button:active { transform: translateY(0); }
        button.danger { background: #ef4444; }
        button.danger:hover { background: #dc2626; }
        button.success { background: #22c55e; }
        button.success:hover { background: #16a34a; }
        button.warning { background: #f59e0b; }
        button.warning:hover { background: #d97706; }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        .stat-item {
            background: #0f172a;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #3b82f6;
        }
        .stat-label {
            color: #94a3b8;
            font-size: 14px;
            margin-bottom: 5px;
        }
        .stat-value {
            color: #22d3ee;
            font-size: 24px;
            font-weight: bold;
            font-family: 'Courier New', monospace;
        }
        
        .content-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        
        #log { 
            background: #0f172a; 
            padding: 20px; 
            border-radius: 8px; 
            max-height: 400px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            border: 1px solid #334155;
        }
        .log-entry { 
            padding: 8px; 
            margin: 5px 0; 
            border-left: 3px solid #3b82f6;
            padding-left: 12px;
            line-height: 1.5;
        }
        .log-entry.success { border-left-color: #22c55e; color: #86efac; }
        .log-entry.error { border-left-color: #ef4444; color: #fca5a5; }
        .log-entry.warning { border-left-color: #fbbf24; color: #fde047; }
        .log-entry.info { border-left-color: #3b82f6; color: #93c5fd; }
        
        .data-preview {
            background: #0f172a;
            padding: 15px;
            border-radius: 8px;
            max-height: 400px;
            overflow-y: auto;
            border: 1px solid #334155;
        }
        .data-preview pre {
            color: #e2e8f0;
            font-size: 12px;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        
        .camera-list {
            background: #0f172a;
            padding: 15px;
            border-radius: 8px;
            max-height: 300px;
            overflow-y: auto;
            border: 1px solid #334155;
        }
        .camera-item {
            background: #1e293b;
            padding: 10px;
            margin: 5px 0;
            border-radius: 6px;
            border-left: 3px solid #22c55e;
        }
        .camera-name {
            color: #22d3ee;
            font-weight: bold;
        }
        .camera-url {
            color: #94a3b8;
            font-size: 12px;
            font-family: 'Courier New', monospace;
        }
        
        ::-webkit-scrollbar { width: 10px; }
        ::-webkit-scrollbar-track { background: #1e293b; }
        ::-webkit-scrollbar-thumb { background: #475569; border-radius: 5px; }
        ::-webkit-scrollbar-thumb:hover { background: #64748b; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📡 消息代理 WebSocket 实时测试</h1>
        
        <div class="status-card">
            <div id="status" class="status disconnected">未连接</div>
            
            <div class="stats">
                <div class="stat-item">
                    <div class="stat-label">接收消息数</div>
                    <div class="stat-value" id="messageCount">0</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">摄像头更新</div>
                    <div class="stat-value" id="cameraUpdateCount">0</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">当前摄像头数</div>
                    <div class="stat-value" id="currentCameraCount">0</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">连接时长</div>
                    <div class="stat-value" id="uptime">0s</div>
                </div>
            </div>
            
            <div class="button-group">
                <button onclick="connect()" class="success">🔗 连接代理 WebSocket</button>
                <button onclick="disconnect()" class="danger">❌ 断开连接</button>
                <button onclick="requestRefresh()" class="warning">🔄 刷新状态</button>
                <button onclick="clearLog()">🗑️ 清除日志</button>
            </div>
        </div>
        
        <div class="content-grid">
            <div class="status-card">
                <h3 style="margin-bottom: 15px; color: #22d3ee;">📝 连接日志</h3>
                <div id="log"></div>
            </div>
            
            <div class="status-card">
                <h3 style="margin-bottom: 15px; color: #22d3ee;">📹 当前摄像头列表</h3>
                <div class="camera-list" id="cameraList">
                    <div style="color: #94a3b8; text-align: center; padding: 20px;">等待连接...</div>
                </div>
            </div>
        </div>
        
        <div class="status-card">
            <h3 style="margin-bottom: 15px; color: #22d3ee;">📊 最新消息数据</h3>
            <div class="data-preview">
                <pre id="dataPreview">等待数据...</pre>
            </div>
        </div>
    </div>

    <script>
        let ws = null;
        let messageCount = 0;
        let cameraUpdateCount = 0;
        let currentCameras = [];
        let connectTime = null;
        let uptimeInterval = null;
        const WS_URL = 'ws://127.0.0.1:8000/api/broker/stream';

        function updateStatus(text, className) {
            const status = document.getElementById('status');
            status.textContent = text;
            status.className = 'status ' + className;
        }

        function updateStats() {
            document.getElementById('messageCount').textContent = messageCount;
            document.getElementById('cameraUpdateCount').textContent = cameraUpdateCount;
            document.getElementById('currentCameraCount').textContent = currentCameras.length;
        }

        function startUptimeCounter() {
            connectTime = Date.now();
            if (uptimeInterval) clearInterval(uptimeInterval);
            uptimeInterval = setInterval(() => {
                if (connectTime) {
                    const seconds = Math.floor((Date.now() - connectTime) / 1000);
                    document.getElementById('uptime').textContent = seconds + 's';
                }
            }, 1000);
        }

        function stopUptimeCounter() {
            if (uptimeInterval) {
                clearInterval(uptimeInterval);
                uptimeInterval = null;
            }
            connectTime = null;
            document.getElementById('uptime').textContent = '0s';
        }

        function log(message, type = 'info') {
            const logDiv = document.getElementById('log');
            const entry = document.createElement('div');
            entry.className = 'log-entry ' + type;
            const timestamp = new Date().toLocaleTimeString('zh-CN', { hour12: false });
            entry.textContent = `[${timestamp}] ${message}`;
            logDiv.insertBefore(entry, logDiv.firstChild);
            console.log(`[${type.toUpperCase()}]`, message);
        }

        function updateDataPreview(data) {
            const preview = document.getElementById('dataPreview');
            preview.textContent = JSON.stringify(data, null, 2);
        }

        function updateCameraList(cameras) {
            const cameraListDiv = document.getElementById('cameraList');
            
            if (!cameras || cameras.length === 0) {
                cameraListDiv.innerHTML = '<div style="color: #94a3b8; text-align: center; padding: 20px;">暂无摄像头</div>';
                return;
            }
            
            let html = '';
            cameras.forEach(camera => {
                html += `
                    <div class="camera-item">
                        <div class="camera-name">${camera.name || camera.id}</div>
                        <div class="camera-url">${camera.url || 'N/A'}</div>
                        <div style="color: #94a3b8; font-size: 11px;">
                            状态: ${camera.status || 'unknown'} | 
                            方向: ${(camera.directions || []).join(', ') || 'none'}
                        </div>
                    </div>
                `;
            });
            
            cameraListDiv.innerHTML = html;
        }

        function clearLog() {
            document.getElementById('log').innerHTML = '';
            messageCount = 0;
            cameraUpdateCount = 0;
            updateStats();
            log('日志已清除', 'info');
        }

        function requestRefresh() {
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send('refresh');
                log('已请求刷新状态', 'info');
            } else {
                log('连接未建立，无法刷新', 'warning');
            }
        }

        function connect() {
            if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
                log('已经连接或正在连接中', 'warning');
                return;
            }

            updateStatus('正在连接...', 'connecting');
            log(`尝试连接到 ${WS_URL}`, 'info');

            try {
                ws = new WebSocket(WS_URL);

                ws.onopen = () => {
                    updateStatus('✓ 已连接', 'connected');
                    log('✓ 消息代理 WebSocket 连接成功!', 'success');
                    startUptimeCounter();
                };

                ws.onmessage = (event) => {
                    messageCount++;
                    try {
                        const data = JSON.parse(event.data);
                        
                        if (data.type === 'current_state') {
                            log('收到当前状态', 'success');
                            if (data.cameras) {
                                currentCameras = data.cameras;
                                updateCameraList(data.cameras);
                            }
                        } else if (data.type === 'direction_result') {
                            cameraUpdateCount++;
                            log(`方向消息: ${data.data.command} -> ${data.cameras.length} 个摄像头`, 'success');
                            currentCameras = data.cameras;
                            updateCameraList(data.cameras);
                        } else if (data.type === 'angle_value') {
                            cameraUpdateCount++;
                            log(`角度消息: ${data.data.angle}° -> ${data.cameras.length} 个摄像头`, 'success');
                            currentCameras = data.cameras;
                            updateCameraList(data.cameras);
                        } else if (data.type === 'ai_alert') {
                            cameraUpdateCount++;
                            log(`AI 报警: ${data.data.alert_type} -> ${data.cameras.length} 个摄像头`, 'warning');
                            currentCameras = data.cameras;
                            updateCameraList(data.cameras);
                        } else if (data.type === 'error') {
                            log(`服务器错误: ${data.data.error}`, 'error');
                        }
                        
                        updateStats();
                        updateDataPreview(data);
                        
                    } catch (e) {
                        log(`解析错误: ${e.message}`, 'error');
                    }
                };

                ws.onerror = (error) => {
                    updateStatus('✗ 连接错误', 'error');
                    log('✗ WebSocket 连接错误', 'error');
                    console.error('WebSocket error:', error);
                    stopUptimeCounter();
                };

                ws.onclose = (event) => {
                    updateStatus('已断开', 'disconnected');
                    const reason = event.reason || '无原因';
                    log(`连接已关闭 (code: ${event.code}, reason: ${reason})`, 'warning');
                    stopUptimeCounter();
                };
            } catch (e) {
                updateStatus('✗ 创建失败', 'error');
                log(`✗ 无法创建 WebSocket: ${e.message}`, 'error');
            }
        }

        function disconnect() {
            if (ws) {
                ws.close();
                ws = null;
                log('主动断开连接', 'info');
            } else {
                log('没有活动的连接', 'warning');
            }
        }

        // 页面加载时显示信息
        window.onload = () => {
            log('消息代理 WebSocket 测试页面已加载', 'info');
            log(`目标地址: ${WS_URL}`, 'info');
            log('点击"连接代理 WebSocket"按钮开始测试', 'info');
        };

        // 页面卸载时断开连接
        window.onbeforeunload = () => {
            if (ws) {
                ws.close();
            }
        };
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)


@app.get("/test/websocket", response_class=HTMLResponse)
async def websocket_test_page():
    """WebSocket 测试页面 - 用于调试 WebSocket 连接"""
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>WebSocket 测试页面</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            padding: 20px; 
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            color: #e2e8f0;
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 { 
            color: #22d3ee; 
            margin-bottom: 30px;
            font-size: 2em;
            text-align: center;
        }
        .status-card {
            background: #1e293b;
            border: 2px solid #334155;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }
        .status { 
            padding: 15px 25px; 
            border-radius: 8px; 
            font-size: 18px;
            font-weight: bold;
            text-align: center;
            margin-bottom: 20px;
            transition: all 0.3s ease;
        }
        .connecting { background: #fbbf24; color: #000; }
        .connected { background: #22c55e; color: #000; }
        .disconnected { background: #64748b; color: #fff; }
        .error { background: #ef4444; color: #fff; }
        
        .button-group {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-bottom: 20px;
        }
        button { 
            padding: 12px 24px; 
            font-size: 16px;
            cursor: pointer; 
            border-radius: 8px;
            border: none;
            background: #3b82f6;
            color: white;
            font-weight: 600;
            transition: all 0.2s ease;
            flex: 1;
            min-width: 150px;
        }
        button:hover { 
            background: #2563eb; 
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(59, 130, 246, 0.4);
        }
        button:active { transform: translateY(0); }
        button.danger { background: #ef4444; }
        button.danger:hover { background: #dc2626; }
        button.success { background: #22c55e; }
        button.success:hover { background: #16a34a; }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        .stat-item {
            background: #0f172a;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #3b82f6;
        }
        .stat-label {
            color: #94a3b8;
            font-size: 14px;
            margin-bottom: 5px;
        }
        .stat-value {
            color: #22d3ee;
            font-size: 24px;
            font-weight: bold;
            font-family: 'Courier New', monospace;
        }
        
        #log { 
            background: #0f172a; 
            padding: 20px; 
            border-radius: 8px; 
            max-height: 500px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            border: 1px solid #334155;
        }
        .log-entry { 
            padding: 8px; 
            margin: 5px 0; 
            border-left: 3px solid #3b82f6;
            padding-left: 12px;
            line-height: 1.5;
        }
        .log-entry.success { border-left-color: #22c55e; color: #86efac; }
        .log-entry.error { border-left-color: #ef4444; color: #fca5a5; }
        .log-entry.warning { border-left-color: #fbbf24; color: #fde047; }
        .log-entry.info { border-left-color: #3b82f6; color: #93c5fd; }
        
        .data-preview {
            background: #0f172a;
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
            max-height: 300px;
            overflow-y: auto;
            border: 1px solid #334155;
        }
        .data-preview pre {
            color: #e2e8f0;
            font-size: 12px;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        
        ::-webkit-scrollbar { width: 10px; }
        ::-webkit-scrollbar-track { background: #1e293b; }
        ::-webkit-scrollbar-thumb { background: #475569; border-radius: 5px; }
        ::-webkit-scrollbar-thumb:hover { background: #64748b; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔌 WebSocket 实时测试页面</h1>
        
        <div class="status-card">
            <div id="status" class="status disconnected">未连接</div>
            
            <div class="stats">
                <div class="stat-item">
                    <div class="stat-label">接收消息数</div>
                    <div class="stat-value" id="messageCount">0</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">传感器数据</div>
                    <div class="stat-value" id="sensorCount">0</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">运动指令</div>
                    <div class="stat-value" id="motionCount">0</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">连接时长</div>
                    <div class="stat-value" id="uptime">0s</div>
                </div>
            </div>
            
            <div class="button-group">
                <button onclick="connect()" class="success">🔗 连接 WebSocket</button>
                <button onclick="disconnect()" class="danger">❌ 断开连接</button>
                <button onclick="clearLog()">🗑️ 清除日志</button>
                <button onclick="toggleDataPreview()">📊 切换数据预览</button>
            </div>
        </div>
        
        <div class="status-card">
            <h3 style="margin-bottom: 15px; color: #22d3ee;">📝 连接日志</h3>
            <div id="log"></div>
        </div>
        
        <div class="status-card" id="dataPreviewCard" style="display: none;">
            <h3 style="margin-bottom: 15px; color: #22d3ee;">📊 最新数据</h3>
            <div class="data-preview">
                <pre id="dataPreview">等待数据...</pre>
            </div>
        </div>
    </div>

    <script>
        let ws = null;
        let messageCount = 0;
        let sensorCount = 0;
        let motionCount = 0;
        let connectTime = null;
        let uptimeInterval = null;
        const WS_URL = 'ws://127.0.0.1:8000/api/sensor/stream';

        function updateStatus(text, className) {
            const status = document.getElementById('status');
            status.textContent = text;
            status.className = 'status ' + className;
        }

        function updateStats() {
            document.getElementById('messageCount').textContent = messageCount;
            document.getElementById('sensorCount').textContent = sensorCount;
            document.getElementById('motionCount').textContent = motionCount;
        }

        function startUptimeCounter() {
            connectTime = Date.now();
            if (uptimeInterval) clearInterval(uptimeInterval);
            uptimeInterval = setInterval(() => {
                if (connectTime) {
                    const seconds = Math.floor((Date.now() - connectTime) / 1000);
                    document.getElementById('uptime').textContent = seconds + 's';
                }
            }, 1000);
        }

        function stopUptimeCounter() {
            if (uptimeInterval) {
                clearInterval(uptimeInterval);
                uptimeInterval = null;
            }
            connectTime = null;
            document.getElementById('uptime').textContent = '0s';
        }

        function log(message, type = 'info') {
            const logDiv = document.getElementById('log');
            const entry = document.createElement('div');
            entry.className = 'log-entry ' + type;
            const timestamp = new Date().toLocaleTimeString('zh-CN', { hour12: false });
            entry.textContent = `[${timestamp}] ${message}`;
            logDiv.insertBefore(entry, logDiv.firstChild);
            console.log(`[${type.toUpperCase()}]`, message);
        }

        function updateDataPreview(data) {
            const preview = document.getElementById('dataPreview');
            preview.textContent = JSON.stringify(data, null, 2);
        }

        function toggleDataPreview() {
            const card = document.getElementById('dataPreviewCard');
            card.style.display = card.style.display === 'none' ? 'block' : 'none';
        }

        function clearLog() {
            document.getElementById('log').innerHTML = '';
            messageCount = 0;
            sensorCount = 0;
            motionCount = 0;
            updateStats();
            log('日志已清除', 'info');
        }

        function connect() {
            if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
                log('已经连接或正在连接中', 'warning');
                return;
            }

            updateStatus('正在连接...', 'connecting');
            log(`尝试连接到 ${WS_URL}`, 'info');

            try {
                ws = new WebSocket(WS_URL);

                ws.onopen = () => {
                    updateStatus('✓ 已连接', 'connected');
                    log('✓ WebSocket 连接成功!', 'success');
                    startUptimeCounter();
                };

                ws.onmessage = (event) => {
                    messageCount++;
                    try {
                        const data = JSON.parse(event.data);
                        
                        if (data.type === 'sensor_data') {
                            sensorCount++;
                            if (sensorCount <= 3) {
                                log(`收到传感器数据 #${sensorCount}`, 'success');
                            }
                        } else if (data.type === 'motion_command') {
                            motionCount++;
                            if (motionCount <= 3) {
                                log(`收到运动指令 #${motionCount}: ${data.data.command}`, 'success');
                            }
                        } else if (data.type === 'error') {
                            log(`服务器错误: ${data.data.error}`, 'error');
                        }
                        
                        updateStats();
                        updateDataPreview(data);
                        
                    } catch (e) {
                        log(`解析错误: ${e.message}`, 'error');
                    }
                };

                ws.onerror = (error) => {
                    updateStatus('✗ 连接错误', 'error');
                    log('✗ WebSocket 连接错误', 'error');
                    console.error('WebSocket error:', error);
                    stopUptimeCounter();
                };

                ws.onclose = (event) => {
                    updateStatus('已断开', 'disconnected');
                    const reason = event.reason || '无原因';
                    log(`连接已关闭 (code: ${event.code}, reason: ${reason})`, 'warning');
                    stopUptimeCounter();
                };
            } catch (e) {
                updateStatus('✗ 创建失败', 'error');
                log(`✗ 无法创建 WebSocket: ${e.message}`, 'error');
            }
        }

        function disconnect() {
            if (ws) {
                ws.close();
                ws = null;
                log('主动断开连接', 'info');
            } else {
                log('没有活动的连接', 'warning');
            }
        }

        // 页面加载时显示信息
        window.onload = () => {
            log('WebSocket 测试页面已加载', 'info');
            log(`目标地址: ${WS_URL}`, 'info');
            log('点击"连接 WebSocket"按钮开始测试', 'info');
        };

        // 页面卸载时断开连接
        window.onbeforeunload = () => {
            if (ws) {
                ws.close();
            }
        };
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
