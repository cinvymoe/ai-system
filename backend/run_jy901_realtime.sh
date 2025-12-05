#!/bin/bash
# JY901 传感器实时采集启动脚本

echo "JY901 传感器实时采集"
echo "===================="
echo ""
echo "请选择运行方式:"
echo "1. 完整示例（交互式菜单）"
echo "2. 快速测试（采集50条数据）"
echo "3. 自定义测试"
echo ""
read -p "请选择 (1-3): " choice

case $choice in
    1)
        echo ""
        echo "启动完整示例..."
        python -m src.collectors.sensors.example_realtime
        ;;
    2)
        echo ""
        read -p "请输入串口名称 (默认: /dev/ttyUSB0): " port
        port=${port:-/dev/ttyUSB0}
        echo "启动快速测试..."
        python test_jy901_realtime.py "$port" 50
        ;;
    3)
        echo ""
        read -p "请输入串口名称 (默认: /dev/ttyUSB0): " port
        port=${port:-/dev/ttyUSB0}
        read -p "请输入采集数量 (默认: 100): " count
        count=${count:-100}
        echo "启动自定义测试..."
        python test_jy901_realtime.py "$port" "$count"
        ;;
    *)
        echo "无效选择"
        exit 1
        ;;
esac
