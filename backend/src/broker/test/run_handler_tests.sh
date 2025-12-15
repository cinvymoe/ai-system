#!/bin/bash

# WebSocket Handler 测试运行脚本

echo "=========================================="
echo "Broker Handler WebSocket 测试"
echo "=========================================="
echo ""
echo "确保后端服务已启动: http://localhost:8000"
echo ""

# 检查 Python 环境
if [ -f "../../.venv/bin/activate" ]; then
    source ../../.venv/bin/activate
    echo "✓ 已激活虚拟环境"
elif [ -f "../../../.venv/bin/activate" ]; then
    source ../../../.venv/bin/activate
    echo "✓ 已激活虚拟环境"
else
    echo "⚠ 未找到虚拟环境，使用系统 Python"
fi

echo ""
echo "选择测试模式:"
echo "1) 自动测试 (运行所有测试用例)"
echo "2) 交互模式 (手动输入消息)"
echo ""
read -p "请选择 [1/2]: " choice

case $choice in
    1)
        echo ""
        echo "运行自动测试..."
        python test_handlers_ws.py
        ;;
    2)
        echo ""
        echo "启动交互模式..."
        python test_handlers_ws.py interactive
        ;;
    *)
        echo "无效选择，运行自动测试..."
        python test_handlers_ws.py
        ;;
esac
