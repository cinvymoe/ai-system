#!/usr/bin/env python3
"""
快速测试脚本：传感器 + MessageBroker 集成

直接运行此脚本测试 JY901 传感器与 MessageBroker 的集成。
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from src.broker.test.test_sensor_integration import SensorBrokerIntegrationTest


async def quick_test():
    """快速测试"""
    print("=" * 70)
    print("快速测试：JY901 传感器 + MessageBroker")
    print("=" * 70)
    
    # 创建测试实例
    test = SensorBrokerIntegrationTest()
    
    try:
        # 设置
        await test.setup()
        
        # 运行测试（采集 30 个样本）
        print("\n提示：测试将采集 30 个传感器样本")
        print("      按 Ctrl+C 可随时中断\n")
        
        await test.run_test(max_samples=30)
        
        print("\n✓ 测试成功完成！")
        
    except FileNotFoundError as e:
        print(f"\n✗ 错误: 找不到数据文件")
        print(f"  {e}")
        print(f"\n请确保数据文件存在: backend/data/jy901_data.txt")
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        await test.cleanup()


if __name__ == "__main__":
    try:
        asyncio.run(quick_test())
    except KeyboardInterrupt:
        print("\n\n测试已中断")
