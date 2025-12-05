"""
Test script for MotionDirectionProcessor

验证 MotionDirectionProcessor 与 MockSensorDevice 的集成
"""

import asyncio
import sys
from pathlib import Path

# Add backend/src and parent directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))
sys.path.insert(0, str(Path(__file__).parent.parent))  # For datahandler

from collectors.sensors.mock_sensor import MockSensorDevice
from collectors.processors.motion_processor import MotionDirectionProcessor


async def test_motion_processor():
    """测试运动方向处理器"""
    
    print("=" * 60)
    print("测试 MotionDirectionProcessor")
    print("=" * 60)
    
    # 创建处理器
    processor = MotionDirectionProcessor()
    print("\n✓ MotionDirectionProcessor 已创建")
    
    # 测试不同的运动模式
    patterns = ['forward', 'backward', 'turn_left', 'turn_right', 'stationary']
    
    for pattern in patterns:
        print(f"\n{'=' * 60}")
        print(f"测试运动模式: {pattern}")
        print(f"{'=' * 60}")
        
        # 创建模拟传感器
        sensor = MockSensorDevice(
            sensor_id=f'test_sensor_{pattern}',
            motion_pattern=pattern,
            config={'interval': 0.1, 'noise_level': 0.01}
        )
        
        # 连接传感器
        connected = await sensor.connect()
        if not connected:
            print(f"✗ 无法连接传感器")
            continue
        
        print(f"✓ 传感器已连接")
        
        # 读取并处理5个数据样本
        for i in range(5):
            try:
                # 读取传感器数据
                sensor_data = await sensor.read_sensor_data()
                
                # 处理数据
                motion_command = processor.process(sensor_data)
                
                # 显示结果
                print(f"\n样本 {i+1}:")
                print(f"  命令: {motion_command.command}")
                print(f"  强度: {motion_command.intensity:.4f}")
                print(f"  角强度: {motion_command.angular_intensity:.4f}")
                print(f"  运动开始: {motion_command.is_motion_start}")
                print(f"  原始方向: {motion_command.raw_direction}")
                
                # 等待一小段时间
                await asyncio.sleep(0.15)
                
            except Exception as e:
                print(f"✗ 处理数据时出错: {e}")
                import traceback
                traceback.print_exc()
        
        # 断开传感器
        await sensor.disconnect()
        print(f"\n✓ 传感器已断开")
        
        # 重置处理器状态
        processor.reset()
    
    print(f"\n{'=' * 60}")
    print("测试完成")
    print(f"{'=' * 60}")


async def test_error_handling():
    """测试错误处理"""
    
    print("\n" + "=" * 60)
    print("测试错误处理")
    print("=" * 60)
    
    processor = MotionDirectionProcessor()
    
    # 测试缺少字段
    print("\n测试 1: 缺少加速度字段")
    incomplete_data = {
        '角速度X(°/s)': 0.0,
        '角速度Y(°/s)': 0.0,
        '角速度Z(°/s)': 0.0,
        '角度X(°)': 0.0,
        '角度Y(°)': 0.0,
        '角度Z(°)': 0.0,
    }
    command = processor.process(incomplete_data)
    print(f"  命令: {command.command}")
    print(f"  错误: {command.metadata.get('error', 'None')}")
    
    # 测试无效数据类型
    print("\n测试 2: 无效数据类型")
    invalid_data = {
        '加速度X(g)': 'invalid',
        '加速度Y(g)': 0.0,
        '加速度Z(g)': -1.0,
        '角速度X(°/s)': 0.0,
        '角速度Y(°/s)': 0.0,
        '角速度Z(°/s)': 0.0,
        '角度X(°)': 0.0,
        '角度Y(°)': 0.0,
        '角度Z(°)': 0.0,
    }
    command = processor.process(invalid_data)
    print(f"  命令: {command.command}")
    print(f"  错误: {command.metadata.get('error', 'None')}")
    
    print("\n✓ 错误处理测试完成")


if __name__ == '__main__':
    # 运行测试
    asyncio.run(test_motion_processor())
    asyncio.run(test_error_handling())
