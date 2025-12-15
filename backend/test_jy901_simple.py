#!/usr/bin/env python3
"""
JY901 传感器简单测试脚本

测试传感器的基本功能：
1. 连接测试
2. 数据读取测试
3. 数据解析测试
4. 传感器校准测试
"""

import asyncio
import sys
from src.collectors.sensors.jy901 import JY901Sensor


async def test_sensor_connection():
    """测试传感器连接"""
    print("=" * 60)
    print("JY901 传感器连接测试")
    print("=" * 60)
    
    sensor = JY901Sensor(
        'test_jy901',
        config={
            'mode': 'realtime',
            'port': '/dev/ttyACM0',
            'baudrate': 9600,
            'timeout': 1.0
        }
    )
    
    print(f"传感器ID: {sensor.get_source_id()}")
    print(f"传感器类型: {sensor.sensor_type}")
    print(f"串口: {sensor.port}")
    print(f"波特率: {sensor.baudrate}")
    
    # 连接测试
    print("\n正在连接传感器...")
    success = await sensor.connect()
    
    if success:
        print("✓ 连接成功！")
        
        # 等待一些数据
        print("\n等待传感器数据...")
        await asyncio.sleep(2)
        
        # 读取数据
        try:
            data = await sensor.read_sensor_data()
            print("✓ 数据读取成功！")
            
            # 显示传感器数据
            print("\n传感器数据:")
            print("-" * 40)
            
            acc = sensor.get_acceleration()
            if acc:
                print(f"加速度: X={acc['x']:.3f}g, Y={acc['y']:.3f}g, Z={acc['z']:.3f}g")
            
            gyro = sensor.get_gyroscope()
            if gyro:
                print(f"角速度: X={gyro['x']:.2f}°/s, Y={gyro['y']:.2f}°/s, Z={gyro['z']:.2f}°/s")
            
            angle = sensor.get_angle()
            if angle:
                print(f"角度: X={angle['x']:.1f}°, Y={angle['y']:.1f}°, Z={angle['z']:.1f}°")
            
            temp = sensor.get_temperature()
            if temp is not None:
                print(f"温度: {temp:.1f}°C")
            
            battery = sensor.get_battery()
            if battery is not None:
                print(f"电量: {battery:.0f}%")
            
        except Exception as e:
            print(f"❌ 数据读取失败: {e}")
        
        # 断开连接
        await sensor.disconnect()
        print("\n✓ 传感器已断开")
        
    else:
        print("❌ 连接失败！")
        print("\n可能的原因:")
        print("1. 传感器未连接到 /dev/ttyACM0")
        print("2. 串口权限不足")
        print("3. 传感器未上电")
        return False
    
    return success


async def test_sensor_calibration():
    """测试传感器校准功能"""
    print("\n" + "=" * 60)
    print("JY901 传感器校准测试")
    print("=" * 60)
    
    sensor = JY901Sensor(
        'calibration_test',
        config={
            'mode': 'realtime',
            'port': '/dev/ttyACM0',
            'baudrate': 9600,
            'timeout': 1.0
        }
    )
    
    if await sensor.connect():
        print("传感器已连接，开始校准测试...")
        
        # 解锁传感器
        print("\n正在解锁传感器...")
        if sensor.unlock():
            print("✓ 传感器解锁成功")
            
            # 加速度校准
            print("\n开始加速度校准...")
            print("请将传感器水平放置并保持静止...")
            
            user_input = input("按 Enter 开始校准，或输入 'skip' 跳过: ")
            if user_input.lower() != 'skip':
                if sensor.calibrate_acceleration():
                    print("✓ 加速度校准完成")
                else:
                    print("❌ 加速度校准失败")
            
            # 磁场校准
            print("\n磁场校准测试...")
            user_input = input("按 Enter 开始磁场校准，或输入 'skip' 跳过: ")
            if user_input.lower() != 'skip':
                if sensor.start_magnetic_calibration():
                    print("✓ 磁场校准已开始")
                    print("请以8字形晃动传感器30秒...")
                    
                    await asyncio.sleep(30)
                    
                    if sensor.end_magnetic_calibration():
                        print("✓ 磁场校准完成")
                    else:
                        print("❌ 磁场校准保存失败")
                else:
                    print("❌ 磁场校准启动失败")
        else:
            print("❌ 传感器解锁失败")
        
        await sensor.disconnect()
    else:
        print("❌ 无法连接传感器")


async def test_data_stream():
    """测试数据流采集"""
    print("\n" + "=" * 60)
    print("JY901 传感器数据流测试")
    print("=" * 60)
    
    sensor = JY901Sensor(
        'stream_test',
        config={
            'mode': 'realtime',
            'port': '/dev/ttyACM0',
            'baudrate': 9600,
            'timeout': 1.0
        }
    )
    
    if await sensor.connect():
        print("开始数据流采集...")
        print("按 Ctrl+C 停止采集")
        
        count = 0
        try:
            async for data in sensor.collect_stream():
                count += 1
                
                # 获取传感器数据
                acc = sensor.get_acceleration()
                gyro = sensor.get_gyroscope()
                temp = sensor.get_temperature()
                
                if acc and gyro:
                    temp_str = f"{temp:5.1f}°C" if temp is not None else "  N/A"
                    print(f"[{count:3d}] Acc: ({acc['x']:6.3f}, {acc['y']:6.3f}, {acc['z']:6.3f}) "
                          f"Gyro: ({gyro['x']:7.2f}, {gyro['y']:7.2f}, {gyro['z']:7.2f}) ")
                
                if count >= 50:  # 最多采集50条数据
                    break
                    
        except KeyboardInterrupt:
            print(f"\n用户中断，已采集 {count} 条数据")
        
        await sensor.disconnect()
        print(f"数据流测试完成，总共采集 {count} 条数据")
    else:
        print("❌ 无法连接传感器")


async def main():
    """主函数"""
    print("JY901 传感器测试套件")
    print("使用串口: /dev/ttyACM0")
    
    # 基本连接测试
    success = await test_sensor_connection()
    
    if success:
        # 询问是否进行更多测试
        print("\n" + "=" * 60)
        print("可选测试:")
        print("1. 传感器校准测试")
        print("2. 数据流采集测试")
        print("3. 退出")
        
        while True:
            choice = input("\n请选择测试项目 (1-3): ").strip()
            
            if choice == '1':
                await test_sensor_calibration()
            elif choice == '2':
                await test_data_stream()
            elif choice == '3':
                break
            else:
                print("无效选择，请输入 1-3")
    
    print("\n测试完成！")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n程序已退出")
    except Exception as e:
        print(f"\n程序错误: {e}")
        sys.exit(1)