#!/bin/bash

# 传感器方向 → 摄像头 URL 实时监控启动脚本

echo "=========================================="
echo "  传感器方向 → 摄像头 URL 实时监控"
echo "=========================================="
echo ""
echo "提示："
echo "  1. 请确保后端服务正在运行"
echo "  2. 请确保 JY901 传感器已连接到 /dev/ttyACM0"
echo "  3. 按 Ctrl+C 退出监控"
echo ""
echo "启动中..."
echo ""

# 运行监控脚本
python test_sensor_direction_cameras.py
