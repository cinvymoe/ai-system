#!/usr/bin/env python3
"""
JY901 传感器实时采集快速测试脚本

使用方法:
    python test_jy901_realtime.py [串口名称] [采集数量]

示例:
    python test_jy901_realtime.py /dev/ttyUSB0 50
    python test_jy901_realtime.py COM3 100
"""

import asyncio
import sys
import platform


def get_default_port():
    """获取默认串口"""
    system = platform.system().lower()
    if system == 'linux':
        return '/dev/ttyUSB0'
    elif system == 'windows':
        return 'COM3'
    else:
        return '/dev/ttyUSB0'


async def test_realtime_sensor(port: str, count: int = 50):
    """测试实时传感器采集"""
    from src.collectors.sensors import JY901Sensor
    
    print("=" * 70)
    print("JY901 传感器实时采集测试")
    print("=" * 70)
    print(f"串口: {port}")
    print(f"波特率: 9600")
    print(f"采集数量: {count}")
    print("=" * 70)
    
    # 创建传感器实例
    sensor = JY901Sensor(
        sensor_id='jy901_test',
        config={
            'mode': 'realtime',
            'port': port,
            'baudrate': 9600,
            'timeout': 0.5
        }
    )
    
    # 连接传感器
    print("\n正在连接传感器...")
    if not await sensor.connect():
        print("❌ 连接失败！")
        print("\n可能的原因:")
        print("1. 串口名称不正确")
        print("2. 传感器未连接")
        print("3. 没有串口访问权限")
        print("\nLinux 用户请尝试:")
        print("  sudo usermod -a -G dialout $USER")
        print("  然后重新登录")
        return False
    
    print("✓ 连接成功！\n")
    
    # 显示表头
    print(f"{'序号':>5} | {'AccX(g)':>8} | {'AccY(g)':>8} | {'AccZ(g)':>8} | "
          f"{'GyroX(°/s)':>10} | {'GyroY(°/s)':>10} | {'GyroZ(°/s)':>10} | "
          f"{'温度(°C)':>8}")
    print("-" * 100)
    
    # 采集数据
    collected = 0
    try:
        async for data in sensor.collect():
            collected += 1
            
            acc = sensor.get_acceleration()
            gyro = sensor.get_gyroscope()
            temp = sensor.get_temperature()
            
            # 格式化输出
            acc_str = f"{acc['x']:8.3f} | {acc['y']:8.3f} | {acc['z']:8.3f}" if acc else "   N/A   |    N/A   |    N/A  "
            gyro_str = f"{gyro['x']:10.2f} | {gyro['y']:10.2f} | {gyro['z']:10.2f}" if gyro else "    N/A    |     N/A    |     N/A   "
            temp_str = f"{temp:8.1f}" if temp is not None else "   N/A  "
            
            print(f"{collected:5d} | {acc_str} | {gyro_str} | {temp_str}")
            
            if collected >= count:
                break
    
    except KeyboardInterrupt:
        print(f"\n\n⚠ 用户中断 (已采集 {collected} 条数据)")
    
    except Exception as e:
        print(f"\n\n❌ 采集错误: {e}")
        return False
    
    finally:
        await sensor.cleanup()
        print("\n✓ 传感器已断开")
    
    print(f"\n总共采集了 {collected} 条数据")
    return True


def main():
    """主函数"""
    # 解析命令行参数
    if len(sys.argv) > 1:
        port = sys.argv[1]
    else:
        port = get_default_port()
    
    if len(sys.argv) > 2:
        try:
            count = int(sys.argv[2])
        except ValueError:
            print(f"错误: 无效的采集数量 '{sys.argv[2]}'")
            sys.exit(1)
    else:
        count = 50
    
    # 运行测试
    try:
        success = asyncio.run(test_realtime_sensor(port, count))
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n程序已退出")
        sys.exit(0)


if __name__ == '__main__':
    main()
