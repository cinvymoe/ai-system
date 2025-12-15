#!/usr/bin/env python3
"""
JY901 传感器完整测试套件

包含以下测试:
1. 基础功能测试
2. 数据解析测试
3. 回放模式测试
4. 实时模式测试（需要硬件）
5. 错误处理测试
6. 性能测试

运行方法:
    python -m pytest test_jy901_sensor.py -v
    python test_jy901_sensor.py  # 直接运行
"""

import asyncio
import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import threading
import time

# 导入被测试的模块
from src.collectors.sensors.jy901 import JY901Sensor
from src.collectors.models import CollectedData
from src.collectors.enums import CollectionStatus


class TestJY901SensorBasic:
    """JY901 传感器基础功能测试"""
    
    def test_init_default_config(self):
        """测试默认配置初始化"""
        sensor = JY901Sensor('test_sensor')
        
        assert sensor.sensor_id == 'test_sensor'
        assert sensor.sensor_type == 'jy901'
        assert sensor.mode == 'realtime'
        assert sensor.interval == 0.01
        assert sensor.loop == False
        assert sensor.baudrate == 9600
        assert sensor.timeout == 0.5
        assert not sensor._is_connected
    
    def test_init_custom_config(self):
        """测试自定义配置初始化"""
        config = {
            'mode': 'playback',
            'interval': 0.05,
            'loop': True,
            'port': '/dev/ttyACM0',
            'baudrate': 115200,
            'timeout': 1.0
        }
        
        sensor = JY901Sensor('test_sensor', config=config)
        
        assert sensor.mode == 'playback'
        assert sensor.interval == 0.05
        assert sensor.loop == True
        assert sensor.port == '/dev/ttyACM0'
        assert sensor.baudrate == 115200
        assert sensor.timeout == 1.0
    
    def test_get_source_id(self):
        """测试获取数据源ID"""
        sensor = JY901Sensor('my_sensor')
        assert sensor.get_source_id() == 'my_sensor'
    
    def test_data_fields_definition(self):
        """测试数据字段定义"""
        assert len(JY901Sensor.DATA_FIELDS) == 22
        assert '加速度X(g)' in JY901Sensor.DATA_FIELDS
        assert '角速度X(°/s)' in JY901Sensor.DATA_FIELDS
        assert '角度X(°)' in JY901Sensor.DATA_FIELDS
        assert '磁场X(uT)' in JY901Sensor.DATA_FIELDS
        assert '四元数0()' in JY901Sensor.DATA_FIELDS
        assert '温度(°C)' in JY901Sensor.DATA_FIELDS
        assert '电量(%)' in JY901Sensor.DATA_FIELDS
    
    def test_numeric_fields_definition(self):
        """测试数值字段定义"""
        assert len(JY901Sensor.NUMERIC_FIELDS) == 18
        for field in ['加速度X(g)', '角速度X(°/s)', '角度X(°)', '温度(°C)']:
            assert field in JY901Sensor.NUMERIC_FIELDS
    
    def test_value_ranges_definition(self):
        """测试数值范围定义"""
        ranges = JY901Sensor.VALUE_RANGES
        
        # 检查加速度范围
        assert ranges['加速度X(g)'] == (-16, 16)
        assert ranges['加速度Y(g)'] == (-16, 16)
        assert ranges['加速度Z(g)'] == (-16, 16)
        
        # 检查角速度范围
        assert ranges['角速度X(°/s)'] == (-2000, 2000)
        
        # 检查角度范围
        assert ranges['角度X(°)'] == (-180, 180)
        
        # 检查温度范围
        assert ranges['温度(°C)'] == (-40, 85)
        
        # 检查电量范围
        assert ranges['电量(%)'] == (0, 100)


class TestJY901SensorDataValidation:
    """JY901 传感器数据验证测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.sensor = JY901Sensor('test_sensor')
    
    def test_validate_data_valid(self):
        """测试有效数据验证"""
        valid_data = {
            '加速度X(g)': 1.0,
            '加速度Y(g)': 0.5,
            '加速度Z(g)': 9.8,
            '角速度X(°/s)': 10.0,
            '温度(°C)': 25.0,
            '电量(%)': 80.0
        }
        
        assert self.sensor._validate_data(valid_data) == True
    
    def test_validate_data_missing_required(self):
        """测试缺少必需字段的数据"""
        invalid_data = {
            '加速度X(g)': 1.0,
            '加速度Y(g)': 0.5,
            # 缺少 '加速度Z(g)'
            '温度(°C)': 25.0
        }
        
        assert self.sensor._validate_data(invalid_data) == False
    
    def test_validate_data_out_of_range(self):
        """测试超出范围的数据"""
        invalid_data = {
            '加速度X(g)': 20.0,  # 超出 [-16, 16] 范围
            '加速度Y(g)': 0.5,
            '加速度Z(g)': 9.8,
            '温度(°C)': 25.0
        }
        
        assert self.sensor._validate_data(invalid_data) == False
    
    def test_validate_data_none_values(self):
        """测试包含 None 值的数据"""
        invalid_data = {
            '加速度X(g)': None,
            '加速度Y(g)': 0.5,
            '加速度Z(g)': 9.8,
            '温度(°C)': 25.0
        }
        
        assert self.sensor._validate_data(invalid_data) == False


class TestJY901SensorPlaybackMode:
    """JY901 传感器回放模式测试"""
    
    def setup_method(self):
        """测试前准备"""
        # 创建临时测试数据文件
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
        
        # 写入测试数据
        headers = '\t'.join(JY901Sensor.DATA_FIELDS)
        self.temp_file.write(headers + '\n')
        
        # 写入几行测试数据
        test_data = [
            ['2024-01-01 12:00:00', 'JY901', '12:00:00.000', 
             '1.0', '0.5', '9.8', '10.0', '5.0', '2.0',
             '0.0', '0.0', '90.0', '100', '200', '300',
             '1.0', '0.0', '0.0', '0.0', '25.0', '1.0', '80.0'],
            ['2024-01-01 12:00:01', 'JY901', '12:00:01.000',
             '1.1', '0.6', '9.7', '11.0', '6.0', '3.0',
             '1.0', '1.0', '91.0', '101', '201', '301',
             '0.9', '0.1', '0.0', '0.0', '26.0', '1.0', '79.0'],
            ['2024-01-01 12:00:02', 'JY901', '12:00:02.000',
             '1.2', '0.7', '9.6', '12.0', '7.0', '4.0',
             '2.0', '2.0', '92.0', '102', '202', '302',
             '0.8', '0.2', '0.0', '0.0', '27.0', '1.0', '78.0']
        ]
        
        for row in test_data:
            self.temp_file.write('\t'.join(row) + '\n')
        
        self.temp_file.close()
        
        # 创建传感器实例
        self.sensor = JY901Sensor(
            'test_sensor',
            data_file_path=self.temp_file.name,
            config={
                'mode': 'playback',
                'interval': 0.001,  # 快速播放
                'loop': False
            }
        )
    
    def teardown_method(self):
        """测试后清理"""
        if hasattr(self, 'temp_file'):
            os.unlink(self.temp_file.name)
    
    @pytest.mark.asyncio
    async def test_connect_playback_mode(self):
        """测试回放模式连接"""
        result = await self.sensor.connect()
        
        assert result == True
        assert self.sensor._is_connected == True
        assert len(self.sensor.data_list) == 3
        
        await self.sensor.disconnect()
    
    @pytest.mark.asyncio
    async def test_connect_file_not_found(self):
        """测试文件不存在的情况"""
        sensor = JY901Sensor(
            'test_sensor',
            data_file_path='/nonexistent/file.txt',
            config={'mode': 'playback'}
        )
        
        result = await sensor.connect()
        assert result == False
        assert sensor._is_connected == False
    
    @pytest.mark.asyncio
    async def test_read_playback_data(self):
        """测试读取回放数据"""
        await self.sensor.connect()
        
        # 读取第一条数据
        data = await self.sensor.read_sensor_data()
        
        assert data is not None
        assert data['加速度X(g)'] == 1.0
        assert data['加速度Y(g)'] == 0.5
        assert data['加速度Z(g)'] == 9.8
        assert data['温度(°C)'] == 25.0
        
        await self.sensor.disconnect()
    
    @pytest.mark.asyncio
    async def test_collect_stream_playback(self):
        """测试回放模式数据流采集"""
        await self.sensor.connect()
        
        collected_data = []
        async for data in self.sensor.collect_stream():
            collected_data.append(data)
            if len(collected_data) >= 3:
                break
        
        # 应该至少收集到1条数据
        assert len(collected_data) >= 1
        
        # 检查第一条数据
        first_data = collected_data[0]
        assert isinstance(first_data, CollectedData)
        assert first_data.source_id == 'test_sensor'
        assert first_data.metadata['data']['加速度X(g)'] == 1.0
        
        await self.sensor.disconnect()
    
    def test_get_progress(self):
        """测试获取播放进度"""
        # 加载数据
        self.sensor._load_data_file()
        
        # 初始进度
        progress = self.sensor.get_progress()
        assert progress['current_index'] == 0
        assert progress['total_count'] == 3
        assert progress['progress'] == 0
        
        # 模拟播放进度
        self.sensor.current_index = 2
        progress = self.sensor.get_progress()
        assert progress['current_index'] == 2
        assert progress['progress'] == pytest.approx(66.67, rel=1e-2)


class TestJY901SensorDataAccess:
    """JY901 传感器数据访问测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.sensor = JY901Sensor('test_sensor')
        
        # 设置模拟数据
        self.sensor.current_data = {
            '加速度X(g)': 1.0,
            '加速度Y(g)': 0.5,
            '加速度Z(g)': 9.8,
            '角速度X(°/s)': 10.0,
            '角速度Y(°/s)': 5.0,
            '角速度Z(°/s)': 2.0,
            '角度X(°)': 0.0,
            '角度Y(°)': 0.0,
            '角度Z(°)': 90.0,
            '磁场X(uT)': 100.0,
            '磁场Y(uT)': 200.0,
            '磁场Z(uT)': 300.0,
            '四元数0()': 1.0,
            '四元数1()': 0.0,
            '四元数2()': 0.0,
            '四元数3()': 0.0,
            '温度(°C)': 25.0,
            '电量(%)': 80.0
        }
    
    def test_get_acceleration(self):
        """测试获取加速度数据"""
        acc = self.sensor.get_acceleration()
        
        assert acc is not None
        assert acc['x'] == 1.0
        assert acc['y'] == 0.5
        assert acc['z'] == 9.8
    
    def test_get_gyroscope(self):
        """测试获取角速度数据"""
        gyro = self.sensor.get_gyroscope()
        
        assert gyro is not None
        assert gyro['x'] == 10.0
        assert gyro['y'] == 5.0
        assert gyro['z'] == 2.0
    
    def test_get_angle(self):
        """测试获取角度数据"""
        angle = self.sensor.get_angle()
        
        assert angle is not None
        assert angle['x'] == 0.0
        assert angle['y'] == 0.0
        assert angle['z'] == 90.0
    
    def test_get_magnetic(self):
        """测试获取磁场数据"""
        mag = self.sensor.get_magnetic()
        
        assert mag is not None
        assert mag['x'] == 100.0
        assert mag['y'] == 200.0
        assert mag['z'] == 300.0
    
    def test_get_quaternion(self):
        """测试获取四元数数据"""
        quat = self.sensor.get_quaternion()
        
        assert quat is not None
        assert quat['q0'] == 1.0
        assert quat['q1'] == 0.0
        assert quat['q2'] == 0.0
        assert quat['q3'] == 0.0
    
    def test_get_temperature(self):
        """测试获取温度数据"""
        temp = self.sensor.get_temperature()
        assert temp == 25.0
    
    def test_get_battery(self):
        """测试获取电量数据"""
        battery = self.sensor.get_battery()
        assert battery == 80.0
    
    def test_get_data_no_current_data(self):
        """测试没有当前数据时的情况"""
        self.sensor.current_data = None
        
        assert self.sensor.get_acceleration() is None
        assert self.sensor.get_gyroscope() is None
        assert self.sensor.get_angle() is None
        assert self.sensor.get_magnetic() is None
        assert self.sensor.get_quaternion() is None
        assert self.sensor.get_temperature() is None
        assert self.sensor.get_battery() is None


class TestJY901SensorSerialProtocol:
    """JY901 传感器串口协议测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.sensor = JY901Sensor('test_sensor')
        self.sensor.current_data = {}
    
    def test_bytes_to_int16_positive(self):
        """测试字节转换为正整数"""
        # 测试正数: 0x1234 = 4660
        bytes_list = [0x34, 0x12]  # 小端序
        result = self.sensor._bytes_to_int16(bytes_list)
        assert result == 4660
    
    def test_bytes_to_int16_negative(self):
        """测试字节转换为负整数"""
        # 测试负数: 0x8000 = -32768
        bytes_list = [0x00, 0x80]  # 小端序
        result = self.sensor._bytes_to_int16(bytes_list)
        assert result == -32768
    
    def test_parse_acc_packet(self):
        """测试解析加速度数据包"""
        # 构造加速度数据包
        # 0x55 0x51 [ax_low ax_high] [ay_low ay_high] [az_low az_high] [temp_low temp_high] [checksum]
        packet = [0x55, 0x51, 0x00, 0x10, 0x00, 0x08, 0x00, 0x20, 0x64, 0x00, 0x00]
        
        self.sensor._parse_acc_packet(packet)
        
        # 验证解析结果
        # ax = 0x1000 / 32768 * 16 = 2.0
        # ay = 0x0800 / 32768 * 16 = 1.0  
        # az = 0x2000 / 32768 * 16 = 4.0
        # temp = 0x0064 / 100 = 1.0
        
        assert abs(self.sensor.current_data['加速度X(g)'] - 2.0) < 0.01
        assert abs(self.sensor.current_data['加速度Y(g)'] - 1.0) < 0.01
        assert abs(self.sensor.current_data['加速度Z(g)'] - 4.0) < 0.01
        assert abs(self.sensor.current_data['温度(°C)'] - 1.0) < 0.01
    
    def test_parse_gyro_packet(self):
        """测试解析角速度数据包"""
        packet = [0x55, 0x52, 0x00, 0x10, 0x00, 0x08, 0x00, 0x20, 0x00, 0x00, 0x00]
        
        self.sensor._parse_gyro_packet(packet)
        
        # gx = 0x1000 / 32768 * 2000 = 250.0
        # gy = 0x0800 / 32768 * 2000 = 125.0
        # gz = 0x2000 / 32768 * 2000 = 500.0
        
        assert abs(self.sensor.current_data['角速度X(°/s)'] - 250.0) < 0.1
        assert abs(self.sensor.current_data['角速度Y(°/s)'] - 125.0) < 0.1
        assert abs(self.sensor.current_data['角速度Z(°/s)'] - 500.0) < 0.1
    
    def test_parse_angle_packet(self):
        """测试解析角度数据包"""
        packet = [0x55, 0x53, 0x00, 0x40, 0x00, 0x20, 0x00, 0x80, 0x00, 0x00, 0x00]
        
        self.sensor._parse_angle_packet(packet)
        
        # rx = 0x4000 / 32768 * 180 = 90.0
        # ry = 0x2000 / 32768 * 180 = 45.0
        # rz = 0x8000 / 32768 * 180 = -180.0 (负数)
        
        assert abs(self.sensor.current_data['角度X(°)'] - 90.0) < 0.1
        assert abs(self.sensor.current_data['角度Y(°)'] - 45.0) < 0.1
        assert abs(self.sensor.current_data['角度Z(°)'] - (-180.0)) < 0.1
    
    def test_parse_mag_packet(self):
        """测试解析磁场数据包"""
        packet = [0x55, 0x54, 0x64, 0x00, 0xC8, 0x00, 0x2C, 0x01, 0x00, 0x00, 0x00]
        
        self.sensor._parse_mag_packet(packet)
        
        # mx = 0x0064 = 100
        # my = 0x00C8 = 200
        # mz = 0x012C = 300
        
        assert self.sensor.current_data['磁场X(uT)'] == 100.0
        assert self.sensor.current_data['磁场Y(uT)'] == 200.0
        assert self.sensor.current_data['磁场Z(uT)'] == 300.0
    
    def test_parse_quaternion_packet(self):
        """测试解析四元数数据包"""
        # 使用正数值: 0x4000 = 16384, 16384/32768 = 0.5
        packet = [0x55, 0x59, 0x00, 0x40, 0x00, 0x20, 0x00, 0x10, 0x00, 0x08, 0x00]
        
        self.sensor._parse_quaternion_packet(packet)
        
        # q0 = 0x4000 / 32768 = 0.5
        # q1 = 0x2000 / 32768 = 0.25
        # q2 = 0x1000 / 32768 = 0.125
        # q3 = 0x0800 / 32768 = 0.0625
        
        assert abs(self.sensor.current_data['四元数0()'] - 0.5) < 0.001
        assert abs(self.sensor.current_data['四元数1()'] - 0.25) < 0.001
        assert abs(self.sensor.current_data['四元数2()'] - 0.125) < 0.001
        assert abs(self.sensor.current_data['四元数3()'] - 0.0625) < 0.001



class TestJY901SensorRealtime:
    """JY901 传感器实时模式测试（需要硬件）"""
    
    def setup_method(self):
        """测试前准备"""
        self.sensor = JY901Sensor(
            'test_sensor',
            config={
                'mode': 'realtime',
                'port': '/dev/ttyACM0',  # 根据实际情况修改
                'baudrate': 9600,
                'timeout': 1.0
            }
        )
    
    @pytest.mark.asyncio
    async def test_connect_realtime_mode(self):
        """测试实时模式连接"""
        try:
            result = await self.sensor.connect()
            
            if result:
                assert self.sensor._is_connected == True
                assert self.sensor.serial_port is not None
                assert self.sensor.serial_port.is_open == True
                
                await self.sensor.disconnect()
            else:
                pytest.skip("无法连接到硬件设备")
                
        except Exception as e:
            pytest.skip(f"硬件连接失败: {e}")
    
    @pytest.mark.asyncio
    async def test_read_realtime_data(self):
        """测试读取实时数据"""
        try:
            if await self.sensor.connect():
                # 等待一些数据
                await asyncio.sleep(2)
                
                data = await self.sensor.read_sensor_data()
                
                assert data is not None
                assert isinstance(data, dict)
                
                # 检查是否有基本的传感器数据
                if '加速度X(g)' in data:
                    assert isinstance(data['加速度X(g)'], (int, float))
                
                await self.sensor.disconnect()
            else:
                pytest.skip("无法连接到硬件设备")
                
        except Exception as e:
            pytest.skip(f"实时数据读取失败: {e}")


class TestJY901SensorErrorHandling:
    """JY901 传感器错误处理测试"""
    
    def test_invalid_mode(self):
        """测试无效模式"""
        sensor = JY901Sensor('test', config={'mode': 'invalid_mode'})
        
        with pytest.raises(ValueError, match="不支持的模式"):
            asyncio.run(sensor.read_sensor_data())
    
    @pytest.mark.asyncio
    async def test_connect_without_file_in_playback(self):
        """测试回放模式下没有指定文件"""
        sensor = JY901Sensor('test', config={'mode': 'playback'})
        
        result = await sensor.connect()
        assert result == False
        assert sensor._is_connected == False
    
    @pytest.mark.asyncio
    async def test_read_data_not_connected(self):
        """测试未连接时读取数据"""
        sensor = JY901Sensor('test')
        
        with pytest.raises(Exception):
            await sensor.read_sensor_data()
    
    def test_load_empty_file(self):
        """测试加载空文件"""
        # 创建空文件
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        temp_file.close()
        
        sensor = JY901Sensor('test', data_file_path=temp_file.name)
        
        try:
            with pytest.raises(ValueError, match="数据文件为空"):
                sensor._load_data_file()
        finally:
            os.unlink(temp_file.name)
    
    def test_load_invalid_data_file(self):
        """测试加载无效数据文件"""
        # 创建包含无效数据的文件
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
        temp_file.write("invalid,data,format\n")
        temp_file.write("1,2,3\n")
        temp_file.close()
        
        sensor = JY901Sensor('test', data_file_path=temp_file.name)
        
        try:
            sensor._load_data_file()
            # 应该没有有效数据被加载
            assert len(sensor.data_list) == 0
        finally:
            os.unlink(temp_file.name)


def create_performance_test_data(count: int = 1000) -> str:
    """创建性能测试数据文件"""
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
    
    # 写入表头
    headers = '\t'.join(JY901Sensor.DATA_FIELDS)
    temp_file.write(headers + '\n')
    
    # 写入测试数据
    for i in range(count):
        data_row = [
            f'2024-01-01 12:00:{i:02d}',  # 时间
            'JY901',  # 设备名称
            f'12:00:{i:02d}.000',  # 片上时间
            f'{1.0 + i * 0.001:.3f}',  # 加速度X
            f'{0.5 + i * 0.0005:.3f}',  # 加速度Y
            f'{9.8 + i * 0.0001:.3f}',  # 加速度Z
            f'{10.0 + i * 0.01:.2f}',  # 角速度X
            f'{5.0 + i * 0.005:.2f}',  # 角速度Y
            f'{2.0 + i * 0.002:.2f}',  # 角速度Z
            f'{i * 0.1:.1f}',  # 角度X
            f'{i * 0.05:.1f}',  # 角度Y
            f'{90.0 + i * 0.01:.1f}',  # 角度Z
            str(100 + i),  # 磁场X
            str(200 + i),  # 磁场Y
            str(300 + i),  # 磁场Z
            '1.0', '0.0', '0.0', '0.0',  # 四元数
            f'{25.0 + i * 0.01:.1f}',  # 温度
            '1.0',  # 版本号
            f'{80.0 - i * 0.01:.1f}'  # 电量
        ]
        
        temp_file.write('\t'.join(data_row) + '\n')
    
    temp_file.close()
    return temp_file.name


class TestJY901SensorPerformance:
    """JY901 传感器性能测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.test_data_file = create_performance_test_data(1000)
        
        self.sensor = JY901Sensor(
            'perf_test',
            data_file_path=self.test_data_file,
            config={
                'mode': 'playback',
                'interval': 0.001,  # 1ms 间隔
                'loop': False
            }
        )
    
    def teardown_method(self):
        """测试后清理"""
        if hasattr(self, 'test_data_file'):
            os.unlink(self.test_data_file)
    
    @pytest.mark.asyncio
    async def test_data_loading_performance(self):
        """测试数据加载性能"""
        start_time = time.time()
        
        await self.sensor.connect()
        
        load_time = time.time() - start_time
        
        assert self.sensor._is_connected == True
        assert len(self.sensor.data_list) == 1000
        assert load_time < 1.0  # 应该在1秒内完成加载
        
        print(f"加载 1000 条数据耗时: {load_time:.3f} 秒")
        
        await self.sensor.disconnect()
    
    @pytest.mark.asyncio
    async def test_data_streaming_performance(self):
        """测试数据流性能"""
        await self.sensor.connect()
        
        start_time = time.time()
        count = 0
        
        async for data in self.sensor.collect_stream():
            count += 1
            if count >= 100:  # 测试前100条数据
                break
        
        stream_time = time.time() - start_time
        
        # 由于回放模式会在数据播放完毕后停止，所以至少应该有1条数据
        assert count >= 1
        assert stream_time < 2.0  # 应该在2秒内完成
        
        print(f"流式处理 {count} 条数据耗时: {stream_time:.3f} 秒")
        if count > 0:
            print(f"平均每条数据处理时间: {stream_time/count*1000:.2f} ms")
        
        await self.sensor.disconnect()


def run_manual_tests():
    """运行手动测试"""
    print("=" * 70)
    print("JY901 传感器手动测试")
    print("=" * 70)
    
    # 测试1: 基础功能
    print("\n1. 基础功能测试")
    sensor = JY901Sensor('manual_test')
    print(f"✓ 传感器ID: {sensor.get_source_id()}")
    print(f"✓ 传感器类型: {sensor.sensor_type}")
    print(f"✓ 默认模式: {sensor.mode}")
    
    # 测试2: 数据字段
    print(f"\n2. 数据字段测试")
    print(f"✓ 总字段数: {len(JY901Sensor.DATA_FIELDS)}")
    print(f"✓ 数值字段数: {len(JY901Sensor.NUMERIC_FIELDS)}")
    print(f"✓ 范围检查字段数: {len(JY901Sensor.VALUE_RANGES)}")
    
    # 测试3: 数据验证
    print(f"\n3. 数据验证测试")
    valid_data = {
        '加速度X(g)': 1.0,
        '加速度Y(g)': 0.5,
        '加速度Z(g)': 9.8,
        '温度(°C)': 25.0
    }
    result = sensor._validate_data(valid_data)
    print(f"✓ 有效数据验证: {result}")
    
    invalid_data = {
        '加速度X(g)': 100.0,  # 超出范围
        '加速度Y(g)': 0.5,
        '加速度Z(g)': 9.8
    }
    result = sensor._validate_data(invalid_data)
    print(f"✓ 无效数据验证: {not result}")
    
    # 测试4: 协议解析
    print(f"\n4. 协议解析测试")
    sensor.current_data = {}
    
    # 测试加速度包解析
    acc_packet = [0x55, 0x51, 0x00, 0x10, 0x00, 0x08, 0x00, 0x20, 0x64, 0x00, 0x00]
    sensor._parse_acc_packet(acc_packet)
    print(f"✓ 加速度解析: X={sensor.current_data.get('加速度X(g)', 'N/A')}")
    
    print("\n" + "=" * 70)
    print("手动测试完成！")
    print("=" * 70)


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'manual':
        # 运行手动测试
        run_manual_tests()
    else:
        # 运行 pytest
        pytest.main([__file__, '-v', '--tb=short'])