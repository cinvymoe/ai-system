#!/bin/bash
# 重启后端服务脚本

echo "正在停止后端服务..."
pkill -f "uvicorn src.main:app"
sleep 2

echo "正在启动后端服务..."
cd "$(dirname "$0")"
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload &

echo "后端服务已启动"
echo "访问测试页面: http://127.0.0.1:8000/test"
echo "WebSocket 测试: http://127.0.0.1:8000/test/websocket"
