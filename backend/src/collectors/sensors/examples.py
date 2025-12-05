"""
JY901 传感器使用示例
"""

import asyncio
from pathlib import Path
from .jy901 import JY901Sensor


async def example_basic_usage():
    """基础使用示例"""
    print("=" * 60)
    print("示例 1: 基础使用")
    print("=" * 60)
    
    # 创建传感器实例
    sensor = JY901Sensor(
        sensor_id='jy901_001',
        data_file_path='datahandler/data/20250529101647.txt',
        config={
            'mode': 'playback',
            'interval': 0.01,
            'loop': False
        }
    )
    
    # 连接传感器
    if not await sensor.connect():
        print("连接传感器失败")
        return
    
    # 采集10条数据
    count = 0
    async for data in sensor.collect():
        count += 1
        
        print(f"\n--- 数据 #{count} ---")
        print(f"状态: {data.status}")
        print(f"时间戳: {data.timestamp}")
        
        # 显示加速度数据
        acc = sensor.get_acceleration()
        if acc:
            print(f"加速度: X={acc['x']:.3f}g, Y={acc['y']:.3f}g, Z={acc['z']:.3f}g")
        
        # 显示角速度数据
        gyro = sensor.get_gyroscope()
        if gyro:
            print(f"角速度: X={gyro['x']:.2f}°/s, Y={gyro['y']:.2f}°/s, Z={gyro['z']:.2f}°/s")
        
        # 显示温度和电量
        temp = sensor.get_temperature()
        battery = sensor.get_battery()
        if temp is not None:
            print(f"温度: {temp:.1f}°C")
        if battery is not None:
            print(f"电量: {battery:.0f}%")
        
        # 显示进度
        progress = sensor.get_progress()
        print(f"进度: {progress['current_index']}/{progress['total_count']} ({progress['progress']:.1f}%)")
        
        if count >= 10:
            break
    
    # 清理资源
    await sensor.cleanup()
    print("\n传感器已关闭")


async def example_continuous_collection():
    """连续采集示例"""
    print("\n" + "=" * 60)
    print("示例 2: 连续采集（前50条数据）")
    print("=" * 60)
    
    sensor = JY901Sensor(
        sensor_id='jy901_002',
        data_file_path='datahandler/data/20250529101647.txt',
        config={
            'mode': 'playback',
            'interval': 0.01,
            'loop': False
        }
    )
    
    await sensor.connect()
    
    count = 0
    async for data in sensor.collect():
        count += 1
        
        # 简化输出
        acc = sensor.get_acceleration()
        if acc:
            print(f"#{count:3d} | AccX: {acc['x']:6.3f}g | AccY: {acc['y']:6.3f}g | AccZ: {acc['z']:6.3f}g")
        
        if count >= 50:
            break
    
    await sensor.cleanup()


async def example_data_analysis():
    """数据分析示例"""
    print("\n" + "=" * 60)
    print("示例 3: 数据分析（统计前100条数据）")
    print("=" * 60)
    
    sensor = JY901Sensor(
        sensor_id='jy901_003',
        data_file_path='datahandler/data/20250529101647.txt',
        config={
            'mode': 'playback',
            'interval': 0.01,
            'loop': False
        }
    )
    
    await sensor.connect()
    
    # 收集数据用于分析
    acc_x_values = []
    acc_y_values = []
    acc_z_values = []
    
    count = 0
    async for data in sensor.collect():
        count += 1
        
        acc = sensor.get_acceleration()
        if acc:
            acc_x_values.append(acc['x'])
            acc_y_values.append(acc['y'])
            acc_z_values.append(acc['z'])
        
        if count >= 100:
            break
    
    # 计算统计信息
    if acc_x_values:
        import statistics
        
        print(f"\n采集了 {len(acc_x_values)} 条数据")
        print("\n加速度统计:")
        print(f"  X轴: 平均={statistics.mean(acc_x_values):.3f}g, "
              f"标准差={statistics.stdev(acc_x_values):.3f}g, "
              f"范围=[{min(acc_x_values):.3f}, {max(acc_x_values):.3f}]g")
        print(f"  Y轴: 平均={statistics.mean(acc_y_values):.3f}g, "
              f"标准差={statistics.stdev(acc_y_values):.3f}g, "
              f"范围=[{min(acc_y_values):.3f}, {max(acc_y_values):.3f}]g")
        print(f"  Z轴: 平均={statistics.mean(acc_z_values):.3f}g, "
              f"标准差={statistics.stdev(acc_z_values):.3f}g, "
              f"范围=[{min(acc_z_values):.3f}, {max(acc_z_values):.3f}]g")
    
    await sensor.cleanup()


async def example_loop_mode():
    """循环播放模式示例"""
    print("\n" + "=" * 60)
    print("示例 4: 循环播放模式（采集150条数据，数据文件会循环）")
    print("=" * 60)
    
    sensor = JY901Sensor(
        sensor_id='jy901_004',
        data_file_path='datahandler/data/20250529101647.txt',
        config={
            'mode': 'playback',
            'interval': 0.01,
            'loop': True  # 启用循环播放
        }
    )
    
    await sensor.connect()
    
    count = 0
    async for data in sensor.collect():
        count += 1
        
        progress = sensor.get_progress()
        acc = sensor.get_acceleration()
        
        if acc:
            print(f"#{count:3d} | 进度: {progress['current_index']:4d}/{progress['total_count']} | "
                  f"AccX: {acc['x']:6.3f}g")
        
        if count >= 150:
            break
    
    await sensor.cleanup()


async def example_all_sensor_data():
    """完整传感器数据示例"""
    print("\n" + "=" * 60)
    print("示例 5: 完整传感器数据（显示所有传感器读数）")
    print("=" * 60)
    
    sensor = JY901Sensor(
        sensor_id='jy901_005',
        data_file_path='datahandler/data/20250529101647.txt',
        config={
            'mode': 'playback',
            'interval': 0.01,
            'loop': False
        }
    )
    
    await sensor.connect()
    
    count = 0
    async for data in sensor.collect():
        count += 1
        
        print(f"\n{'=' * 60}")
        print(f"数据 #{count}")
        print(f"{'=' * 60}")
        
        # 加速度
        acc = sensor.get_acceleration()
        if acc:
            print(f"加速度:")
            print(f"  X: {acc['x']:7.3f} g")
            print(f"  Y: {acc['y']:7.3f} g")
            print(f"  Z: {acc['z']:7.3f} g")
        
        # 角速度
        gyro = sensor.get_gyroscope()
        if gyro:
            print(f"角速度:")
            print(f"  X: {gyro['x']:8.2f} °/s")
            print(f"  Y: {gyro['y']:8.2f} °/s")
            print(f"  Z: {gyro['z']:8.2f} °/s")
        
        # 角度
        angle = sensor.get_angle()
        if angle:
            print(f"角度:")
            print(f"  X: {angle['x']:7.2f} °")
            print(f"  Y: {angle['y']:7.2f} °")
            print(f"  Z: {angle['z']:7.2f} °")
        
        # 磁场
        mag = sensor.get_magnetic()
        if mag:
            print(f"磁场:")
            print(f"  X: {mag['x']:8.2f} uT")
            print(f"  Y: {mag['y']:8.2f} uT")
            print(f"  Z: {mag['z']:8.2f} uT")
        
        # 四元数
        quat = sensor.get_quaternion()
        if quat:
            print(f"四元数:")
            print(f"  Q0: {quat['q0']:7.5f}")
            print(f"  Q1: {quat['q1']:7.5f}")
            print(f"  Q2: {quat['q2']:7.5f}")
            print(f"  Q3: {quat['q3']:7.5f}")
        
        # 温度和电量
        temp = sensor.get_temperature()
        battery = sensor.get_battery()
        if temp is not None:
            print(f"温度: {temp:.1f} °C")
        if battery is not None:
            print(f"电量: {battery:.0f} %")
        
        if count >= 3:
            break
    
    await sensor.cleanup()


async def main():
    """运行所有示例"""
    # 运行示例 1
    await example_basic_usage()
    
    # 运行示例 2
    await example_continuous_collection()
    
    # 运行示例 3
    await example_data_analysis()
    
    # 运行示例 4
    await example_loop_mode()
    
    # 运行示例 5
    await example_all_sensor_data()


if __name__ == '__main__':
    asyncio.run(main())
