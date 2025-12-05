"""
JY901 传感器实时数据采集示例

本示例展示如何通过串口实时采集 JY901 传感器数据
"""

import asyncio
import sys
import platform
from typing import Optional
from .jy901 import JY901Sensor


def get_default_port() -> str:
    """根据操作系统获取默认串口"""
    system = platform.system().lower()
    if system == 'linux':
        return '/dev/ttyS10'
    elif system == 'windows':
        return 'COM3'
    elif system == 'darwin':  # macOS
        return '/dev/tty.usbserial'
    else:
        return '/dev/ttyUSB0'


async def example_realtime_basic():
    """基础实时采集示例"""
    print("=" * 60)
    print("示例 1: 基础实时采集")
    print("=" * 60)
    
    # 获取串口名称
    port = input(f"请输入串口名称 (默认: {get_default_port()}): ").strip()
    if not port:
        port = get_default_port()
    
    # 创建传感器实例
    sensor = JY901Sensor(
        sensor_id='jy901_realtime_001',
        config={
            'mode': 'realtime',
            'port': port,
            'baudrate': 115200,
            'timeout': 0.5
        }
    )
    
    print(f"\n正在连接到串口: {port} @ 115200 bps...")
    
    # 连接传感器
    if not await sensor.connect():
        print("连接传感器失败，请检查:")
        print("1. 串口名称是否正确")
        print("2. 传感器是否已连接")
        print("3. 是否有串口访问权限 (Linux 需要 sudo 或加入 dialout 组)")
        return
    
    print("连接成功！开始采集数据...\n")
    
    # 采集20条数据
    count = 0
    try:
        async for data in sensor.collect():
            count += 1
            
            print(f"\n{'=' * 60}")
            print(f"数据 #{count}")
            print(f"{'=' * 60}")
            print(f"状态: {data.status}")
            print(f"时间戳: {data.timestamp}")
            
            # 显示加速度数据
            acc = sensor.get_acceleration()
            if acc:
                print(f"\n加速度:")
                print(f"  X: {acc['x']:7.3f} g")
                print(f"  Y: {acc['y']:7.3f} g")
                print(f"  Z: {acc['z']:7.3f} g")
            
            # 显示角速度数据
            gyro = sensor.get_gyroscope()
            if gyro:
                print(f"\n角速度:")
                print(f"  X: {gyro['x']:8.2f} °/s")
                print(f"  Y: {gyro['y']:8.2f} °/s")
                print(f"  Z: {gyro['z']:8.2f} °/s")
            
            # 显示角度数据
            angle = sensor.get_angle()
            if angle:
                print(f"\n角度:")
                print(f"  X: {angle['x']:7.2f} °")
                print(f"  Y: {angle['y']:7.2f} °")
                print(f"  Z: {angle['z']:7.2f} °")
            
            # 显示温度
            temp = sensor.get_temperature()
            if temp is not None:
                print(f"\n温度: {temp:.1f} °C")
            
            if count >= 20:
                break
    
    except KeyboardInterrupt:
        print("\n\n用户中断采集")
    
    finally:
        # 清理资源
        await sensor.cleanup()
        print("\n传感器已断开")


async def example_realtime_continuous():
    """连续实时采集示例（简化输出）"""
    print("\n" + "=" * 60)
    print("示例 2: 连续实时采集（简化输出）")
    print("=" * 60)
    
    port = input(f"请输入串口名称 (默认: {get_default_port()}): ").strip()
    if not port:
        port = get_default_port()
    
    sensor = JY901Sensor(
        sensor_id='jy901_realtime_002',
        config={
            'mode': 'realtime',
            'port': port,
            'baudrate': 9600
        }
    )
    
    print(f"\n正在连接到串口: {port}...")
    
    if not await sensor.connect():
        print("连接失败")
        return
    
    print("连接成功！按 Ctrl+C 停止采集\n")
    print(f"{'序号':>4} | {'AccX':>8} | {'AccY':>8} | {'AccZ':>8} | {'温度':>6}")
    print("-" * 60)
    
    count = 0
    try:
        async for data in sensor.collect():
            count += 1
            
            acc = sensor.get_acceleration()
            temp = sensor.get_temperature()
            
            if acc:
                temp_str = f"{temp:.1f}" if temp is not None else "N/A"
                print(f"{count:4d} | {acc['x']:8.3f} | {acc['y']:8.3f} | {acc['z']:8.3f} | {temp_str:>6}")
            
            # 每100条数据暂停一下
            if count % 100 == 0:
                print(f"\n已采集 {count} 条数据，继续...")
    
    except KeyboardInterrupt:
        print(f"\n\n总共采集了 {count} 条数据")
    
    finally:
        await sensor.cleanup()


async def example_realtime_with_calibration():
    """带校准功能的实时采集示例"""
    print("\n" + "=" * 60)
    print("示例 3: 传感器校准")
    print("=" * 60)
    
    port = input(f"请输入串口名称 (默认: {get_default_port()}): ").strip()
    if not port:
        port = get_default_port()
    
    sensor = JY901Sensor(
        sensor_id='jy901_realtime_003',
        config={
            'mode': 'realtime',
            'port': port,
            'baudrate': 9600
        }
    )
    
    print(f"\n正在连接到串口: {port}...")
    
    if not await sensor.connect():
        print("连接失败")
        return
    
    print("连接成功！\n")
    
    # 显示菜单
    while True:
        print("\n" + "=" * 60)
        print("传感器校准菜单")
        print("=" * 60)
        print("1. 加速度校准（需要传感器水平静止）")
        print("2. 开始磁场校准（需要8字形晃动传感器）")
        print("3. 结束磁场校准")
        print("4. 采集10条数据查看")
        print("5. 退出")
        print("=" * 60)
        
        choice = input("请选择操作 (1-5): ").strip()
        
        if choice == '1':
            print("\n请将传感器水平放置并保持静止...")
            input("准备好后按回车开始校准...")
            
            if sensor.calibrate_acceleration():
                print("✓ 加速度校准完成")
            else:
                print("✗ 加速度校准失败")
        
        elif choice == '2':
            print("\n准备开始磁场校准...")
            input("准备好后按回车开始...")
            
            if sensor.start_magnetic_calibration():
                print("✓ 磁场校准已开始")
                print("请以8字形晃动传感器约30秒...")
                print("完成后选择菜单选项3结束校准")
            else:
                print("✗ 启动磁场校准失败")
        
        elif choice == '3':
            if sensor.end_magnetic_calibration():
                print("✓ 磁场校准已完成并保存")
            else:
                print("✗ 结束磁场校准失败")
        
        elif choice == '4':
            print("\n采集10条数据...")
            count = 0
            async for data in sensor.collect():
                count += 1
                
                acc = sensor.get_acceleration()
                gyro = sensor.get_gyroscope()
                angle = sensor.get_angle()
                
                print(f"\n数据 #{count}:")
                if acc:
                    print(f"  加速度: X={acc['x']:6.3f}g, Y={acc['y']:6.3f}g, Z={acc['z']:6.3f}g")
                if gyro:
                    print(f"  角速度: X={gyro['x']:7.2f}°/s, Y={gyro['y']:7.2f}°/s, Z={gyro['z']:7.2f}°/s")
                if angle:
                    print(f"  角度:   X={angle['x']:6.2f}°, Y={angle['y']:6.2f}°, Z={angle['z']:6.2f}°")
                
                if count >= 10:
                    break
        
        elif choice == '5':
            print("\n退出程序...")
            break
        
        else:
            print("\n无效选择，请重新输入")
    
    await sensor.cleanup()
    print("传感器已断开")


async def example_realtime_data_logging():
    """实时数据记录示例"""
    print("\n" + "=" * 60)
    print("示例 4: 实时数据记录到文件")
    print("=" * 60)
    
    port = input(f"请输入串口名称 (默认: {get_default_port()}): ").strip()
    if not port:
        port = get_default_port()
    
    # 输出文件名
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"jy901_data_{timestamp}.txt"
    
    sensor = JY901Sensor(
        sensor_id='jy901_realtime_004',
        config={
            'mode': 'realtime',
            'port': port,
            'baudrate': 9600
        }
    )
    
    print(f"\n正在连接到串口: {port}...")
    
    if not await sensor.connect():
        print("连接失败")
        return
    
    print(f"连接成功！数据将保存到: {output_file}")
    print("按 Ctrl+C 停止记录\n")
    
    # 打开文件写入
    with open(output_file, 'w', encoding='utf-8') as f:
        # 写入表头
        f.write("时间\t加速度X(g)\t加速度Y(g)\t加速度Z(g)\t")
        f.write("角速度X(°/s)\t角速度Y(°/s)\t角速度Z(°/s)\t")
        f.write("角度X(°)\t角度Y(°)\t角度Z(°)\t")
        f.write("磁场X(uT)\t磁场Y(uT)\t磁场Z(uT)\t")
        f.write("四元数0\t四元数1\t四元数2\t四元数3\t")
        f.write("温度(°C)\n")
        
        count = 0
        try:
            async for data in sensor.collect():
                count += 1
                
                # 获取所有数据
                acc = sensor.get_acceleration()
                gyro = sensor.get_gyroscope()
                angle = sensor.get_angle()
                mag = sensor.get_magnetic()
                quat = sensor.get_quaternion()
                temp = sensor.get_temperature()
                
                # 写入文件
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                f.write(f"{timestamp}\t")
                
                if acc:
                    f.write(f"{acc['x']:.4f}\t{acc['y']:.4f}\t{acc['z']:.4f}\t")
                else:
                    f.write("\t\t\t")
                
                if gyro:
                    f.write(f"{gyro['x']:.4f}\t{gyro['y']:.4f}\t{gyro['z']:.4f}\t")
                else:
                    f.write("\t\t\t")
                
                if angle:
                    f.write(f"{angle['x']:.3f}\t{angle['y']:.3f}\t{angle['z']:.3f}\t")
                else:
                    f.write("\t\t\t")
                
                if mag:
                    f.write(f"{mag['x']:.0f}\t{mag['y']:.0f}\t{mag['z']:.0f}\t")
                else:
                    f.write("\t\t\t")
                
                if quat:
                    f.write(f"{quat['q0']:.5f}\t{quat['q1']:.5f}\t{quat['q2']:.5f}\t{quat['q3']:.5f}\t")
                else:
                    f.write("\t\t\t\t")
                
                if temp is not None:
                    f.write(f"{temp:.2f}\n")
                else:
                    f.write("\n")
                
                # 每10条数据刷新一次
                if count % 10 == 0:
                    f.flush()
                    print(f"已记录 {count} 条数据...", end='\r')
        
        except KeyboardInterrupt:
            print(f"\n\n总共记录了 {count} 条数据到 {output_file}")
        
        finally:
            await sensor.cleanup()


async def main():
    """主函数"""
    print("JY901 传感器实时数据采集示例")
    print("=" * 60)
    print("\n请选择示例:")
    print("1. 基础实时采集")
    print("2. 连续实时采集（简化输出）")
    print("3. 传感器校准")
    print("4. 实时数据记录到文件")
    print("5. 运行所有示例")
    print("=" * 60)
    
    choice = input("\n请选择 (1-5): ").strip()
    
    if choice == '1':
        await example_realtime_basic()
    elif choice == '2':
        await example_realtime_continuous()
    elif choice == '3':
        await example_realtime_with_calibration()
    elif choice == '4':
        await example_realtime_data_logging()
    elif choice == '5':
        await example_realtime_basic()
        await example_realtime_continuous()
        await example_realtime_with_calibration()
        await example_realtime_data_logging()
    else:
        print("无效选择")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n程序已退出")
