#!/usr/bin/env python3
"""
测试完整的数据流：
1. 传感器 WebSocket (ws://localhost:8000/api/sensor/stream) 发布数据
2. Broker WebSocket (ws://localhost:8000/api/broker/stream) 接收摄像头更新

运行此脚本前，请确保后端服务已启动：
cd backend
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
"""

import asyncio
