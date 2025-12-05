"""
Mock Sensor Device

模拟JY901传感器，生成加速度、角速度和角度数据用于测试。
支持5种基础运动模式：stationary, forward, backward, turn_left, turn_right
支持自动切换模式：sequence（按序列切换）, random（随机切换）
"""

import asyncio
import json
import threading
import time
from datetime import datetime
from typing import Any, AsyncIterator, Dict, Optional

import numpy as np

from .base import BaseSensorCollector
from ..models import CollectedData
from ..enums import CollectionStatus


class MockSensorDevice(BaseSensorCollector):
    """模拟传感器设备，生成符合JY901格式的模拟数据"""
    
    # 传感器数据范围
    ACC_RANGE = 16.0  # ±16g
    GYRO_RANGE = 2000.0  # ±2000°/s
    ANGLE_RANGE = 180.0  # ±180°
    
    # 支持的运动模式
    VALID_PATTERNS = ['forward', 'backward', 'turn_left', 'turn_right', 'stationary', 'sequence', 'random']
    
    def __init__(
        self,
        sensor_id: str,
        motion_pattern: str = 'stationary',
        config: Optional[Dict[str, Any]] = None
    ):
        """
        初始化模拟传感器设备
        
        Args:
            sensor_id: 传感器唯一标识
            motion_pattern: 运动模式
                - 基础模式: 'stationary', 'forward', 'backward', 'turn_left', 'turn_right'
                - 自动模式: 'sequence'（按序列切换）, 'random'（随机切换）
            config: 配置参数
                - interval: 数据生成间隔（秒，默认0.1）
                - noise_level: 噪声标准差（默认0.01）
        """
        super().__init__(sensor_id, 'mock_sensor', config)
        
        # 运动模式
        self.motion_pattern = motion_pattern if motion_pattern in self.VALID_PATTERNS else 'stationary'
        if motion_pattern not in self.VALID_PATTERNS:
            print(f"警告: 无效的运动模式 '{motion_pattern}'，使用默认值 'stationary'")
        
        # 配置参数
        self.interval = self.config.get('interval', 0.1)
        if self.interval <= 0:
            print(f"警告: 无效的间隔值 {self.interval}，使用默认值 0.1")
            self.interval = 0.1
        
        self.noise_level = self.config.get('noise_level', 0.01)
        if self.noise_level < 0:
            print(f"警告: 无效的噪声级别 {self.noise_level}，使用默认值 0.01")
            self.noise_level = 0.01
        
        # 线程控制
        self.is_running = False
        self.generation_thread: Optional[threading.Thread] = None
        self.data_lock = threading.Lock()
        
        # 当前数据缓存
        self.current_data: Optional[Dict[str, Any]] = None
        
        # 运动状态（用于角度累积）
        self.current_angle_z = 0.0
        
        # 序列模式相关
        self.sequence_patterns = ['stationary', 'forward', 'turn_right', 'forward', 'turn_left', 'backward', 'stationary']
        self.sequence_index = 0
        self.sequence_counter = 0
        self.sequence_duration = 30  # 每个模式持续30个周期（约3秒）
        
        # 随机模式相关
        self.random_counter = 0
        self.random_duration = 50  # 每个随机模式持续50个周期（约5秒）
        self.current_random_pattern = 'stationary'
    
    async def connect(self) -> bool:
        """连接到模拟传感器"""
        try:
            print(f"MockSensorDevice [{self.sensor_id}] 已连接，运动模式: {self.motion_pattern}")
            self._is_connected = True
            return True
        except Exception as e:
            print(f"连接 MockSensorDevice 失败: {e}")
            return False
    
    async def disconnect(self) -> None:
        """断开模拟传感器连接"""
        self.is_running = False
        
        # 等待线程结束
        if self.generation_thread and self.generation_thread.is_alive():
            self.generation_thread.join(timeout=1.0)
        
        self._is_connected = False
        print(f"MockSensorDevice [{self.sensor_id}] 已断开")
    
    async def read_sensor_data(self) -> Dict[str, Any]:
        """
        读取传感器数据
        
        Returns:
            Dict[str, Any]: 传感器数据字典
        """
        if not self.is_running:
            # 启动数据生成线程
            self.is_running = True
            self.generation_thread = threading.Thread(
                target=self._data_generation_loop,
                daemon=True
            )
            self.generation_thread.start()
        
        # 等待数据可用
        max_wait = 10  # 最多等待10秒
        wait_count = 0
        while self.current_data is None and wait_count < max_wait * 100:
            await asyncio.sleep(0.01)
            wait_count += 1
        
        if self.current_data is None:
            raise TimeoutError("等待数据超时")
        
        # 返回当前数据的副本
        with self.data_lock:
            data = self.current_data.copy() if self.current_data else {}
        
        return data
    
    async def collect_stream(self) -> AsyncIterator[CollectedData]:
        """
        采集数据流（实现 IDataSource 接口）
        
        Yields:
            CollectedData: 持续采集的数据
        """
        if not self._is_connected:
            await self.connect()
        
        # Start data generation if not already running
        if not self.is_running:
            self.is_running = True
            self.generation_thread = threading.Thread(
                target=self._data_generation_loop,
                daemon=True
            )
            self.generation_thread.start()
        
        while self._is_connected and self.is_running:
            try:
                raw_data = await self.read_sensor_data()
                
                # 验证数据不为空
                if not raw_data:
                    print(f"警告: read_sensor_data返回空数据")
                    await asyncio.sleep(self.interval)
                    continue
                
                # 将数据转换为JSON字节
                try:
                    raw_bytes = json.dumps(raw_data, ensure_ascii=False).encode('utf-8')
                except (TypeError, ValueError) as e:
                    print(f"JSON序列化错误: {e}, 数据: {raw_data}")
                    await asyncio.sleep(self.interval)
                    continue
                
                yield CollectedData(
                    source_id=self.sensor_id,
                    timestamp=datetime.now(),
                    data_format='json',
                    collection_method='mock_stream',
                    raw_data=raw_bytes,
                    metadata={
                        'sensor_type': self.sensor_type,
                        'sensor_id': self.sensor_id,
                        'collection_time': datetime.now().isoformat(),
                        'motion_pattern': self.motion_pattern,
                    }
                )
                
                await asyncio.sleep(self.interval)
                
            except Exception as e:
                print(f"collect_stream错误: {e}")
                # 不要yield错误数据，而是记录并继续
                await asyncio.sleep(self.interval)
                continue
    
    def get_source_id(self) -> str:
        """
        获取数据源唯一标识（实现 IDataSource 接口）
        
        Returns:
            str: 传感器ID
        """
        return self.sensor_id
    
    def set_motion_pattern(self, pattern: str) -> None:
        """
        设置运动模式
        
        Args:
            pattern: 运动模式
        """
        if pattern in self.VALID_PATTERNS:
            self.motion_pattern = pattern
            print(f"运动模式已更改为: {pattern}")
        else:
            print(f"警告: 无效的运动模式 '{pattern}'")
    
    def _data_generation_loop(self):
        """数据生成循环（在独立线程中运行）"""
        print(f"MockSensorDevice [{self.sensor_id}] 数据生成线程已启动")
        
        while self.is_running:
            try:
                # 获取当前有效的运动模式
                current_pattern = self._get_current_pattern()
                
                # 根据运动模式生成数据
                if current_pattern == 'forward':
                    data = self._generate_forward_data()
                elif current_pattern == 'backward':
                    data = self._generate_backward_data()
                elif current_pattern == 'turn_left':
                    data = self._generate_turn_left_data()
                elif current_pattern == 'turn_right':
                    data = self._generate_turn_right_data()
                else:  # stationary
                    data = self._generate_stationary_data()
                
                # 更新当前数据缓存
                with self.data_lock:
                    self.current_data = data
                
                # 等待指定间隔
                time.sleep(self.interval)
                
            except Exception as e:
                print(f"数据生成错误: {e}")
                time.sleep(self.interval)
        
        print(f"MockSensorDevice [{self.sensor_id}] 数据生成线程已停止")
    
    def _get_current_pattern(self) -> str:
        """获取当前有效的运动模式（处理sequence和random模式）"""
        if self.motion_pattern == 'sequence':
            # 序列模式：按顺序切换
            self.sequence_counter += 1
            if self.sequence_counter >= self.sequence_duration:
                self.sequence_counter = 0
                self.sequence_index = (self.sequence_index + 1) % len(self.sequence_patterns)
                pattern = self.sequence_patterns[self.sequence_index]
                print(f"序列模式切换到: {pattern}")
            return self.sequence_patterns[self.sequence_index]
        
        elif self.motion_pattern == 'random':
            # 随机模式：随机切换
            self.random_counter += 1
            if self.random_counter >= self.random_duration:
                self.random_counter = 0
                # 从5种基础模式中随机选择
                basic_patterns = ['stationary', 'forward', 'backward', 'turn_left', 'turn_right']
                self.current_random_pattern = np.random.choice(basic_patterns)
                print(f"随机模式切换到: {self.current_random_pattern}")
            return self.current_random_pattern
        
        else:
            return self.motion_pattern
    
    def _generate_forward_data(self) -> Dict[str, Any]:
        """生成前进运动模式数据"""
        # 前进：X轴正向加速度 (0.1~0.3g)
        acc_x = 0.2 + self._add_noise(0.1)
        acc_y = self._add_noise(0.02)
        acc_z = -1.0 + self._add_noise(0.02)  # 重力
        
        # 微小角速度波动
        gyro_x = self._add_noise(0.5)
        gyro_y = self._add_noise(0.5)
        gyro_z = self._add_noise(0.5)
        
        # 角度保持稳定
        angle_x = self._add_noise(1.0)
        angle_y = self._add_noise(1.0)
        angle_z = self.current_angle_z + self._add_noise(0.5)
        
        return self._create_sensor_data(
            acc_x, acc_y, acc_z,
            gyro_x, gyro_y, gyro_z,
            angle_x, angle_y, angle_z
        )
    
    def _generate_backward_data(self) -> Dict[str, Any]:
        """生成后退运动模式数据"""
        # 后退：X轴负向加速度 (-0.3~-0.1g)
        acc_x = -0.2 + self._add_noise(0.1)
        acc_y = self._add_noise(0.02)
        acc_z = -1.0 + self._add_noise(0.02)  # 重力
        
        # 微小角速度波动
        gyro_x = self._add_noise(0.5)
        gyro_y = self._add_noise(0.5)
        gyro_z = self._add_noise(0.5)
        
        # 角度保持稳定
        angle_x = self._add_noise(1.0)
        angle_y = self._add_noise(1.0)
        angle_z = self.current_angle_z + self._add_noise(0.5)
        
        return self._create_sensor_data(
            acc_x, acc_y, acc_z,
            gyro_x, gyro_y, gyro_z,
            angle_x, angle_y, angle_z
        )
    
    def _generate_turn_left_data(self) -> Dict[str, Any]:
        """生成左转运动模式数据"""
        # 微小线性加速度
        acc_x = self._add_noise(0.05)
        acc_y = self._add_noise(0.05)
        acc_z = -1.0 + self._add_noise(0.02)  # 重力
        
        # Z轴负向旋转 (-30~-10°/s)
        gyro_x = self._add_noise(1.0)
        gyro_y = self._add_noise(1.0)
        gyro_z = -20.0 + self._add_noise(10.0)
        
        # Z轴角度递减
        self.current_angle_z -= 2.0  # 每次减少2度
        if self.current_angle_z < -180.0:
            self.current_angle_z += 360.0
        
        angle_x = self._add_noise(1.0)
        angle_y = self._add_noise(1.0)
        angle_z = self.current_angle_z + self._add_noise(0.5)
        
        return self._create_sensor_data(
            acc_x, acc_y, acc_z,
            gyro_x, gyro_y, gyro_z,
            angle_x, angle_y, angle_z
        )
    
    def _generate_turn_right_data(self) -> Dict[str, Any]:
        """生成右转运动模式数据"""
        # 微小线性加速度
        acc_x = self._add_noise(0.05)
        acc_y = self._add_noise(0.05)
        acc_z = -1.0 + self._add_noise(0.02)  # 重力
        
        # Z轴正向旋转 (10~30°/s)
        gyro_x = self._add_noise(1.0)
        gyro_y = self._add_noise(1.0)
        gyro_z = 20.0 + self._add_noise(10.0)
        
        # Z轴角度递增
        self.current_angle_z += 2.0  # 每次增加2度
        if self.current_angle_z > 180.0:
            self.current_angle_z -= 360.0
        
        angle_x = self._add_noise(1.0)
        angle_y = self._add_noise(1.0)
        angle_z = self.current_angle_z + self._add_noise(0.5)
        
        return self._create_sensor_data(
            acc_x, acc_y, acc_z,
            gyro_x, gyro_y, gyro_z,
            angle_x, angle_y, angle_z
        )
    
    def _generate_stationary_data(self) -> Dict[str, Any]:
        """生成静止运动模式数据"""
        # 仅重力加速度
        acc_x = self._add_noise(0.01)
        acc_y = self._add_noise(0.01)
        acc_z = -1.0 + self._add_noise(0.01)  # 重力
        
        # 接近零的角速度
        gyro_x = self._add_noise(0.1)
        gyro_y = self._add_noise(0.1)
        gyro_z = self._add_noise(0.1)
        
        # 角度保持稳定
        angle_x = self._add_noise(0.5)
        angle_y = self._add_noise(0.5)
        angle_z = self.current_angle_z + self._add_noise(0.2)
        
        return self._create_sensor_data(
            acc_x, acc_y, acc_z,
            gyro_x, gyro_y, gyro_z,
            angle_x, angle_y, angle_z
        )
    
    def _add_noise(self, scale: float) -> float:
        """
        添加高斯噪声
        
        Args:
            scale: 噪声幅度
            
        Returns:
            float: 噪声值
        """
        return np.random.normal(0, self.noise_level * scale)
    
    def _create_sensor_data(
        self,
        acc_x: float, acc_y: float, acc_z: float,
        gyro_x: float, gyro_y: float, gyro_z: float,
        angle_x: float, angle_y: float, angle_z: float
    ) -> Dict[str, Any]:
        """
        创建传感器数据字典
        
        Args:
            acc_x, acc_y, acc_z: 加速度 (g)
            gyro_x, gyro_y, gyro_z: 角速度 (°/s)
            angle_x, angle_y, angle_z: 角度 (°)
            
        Returns:
            Dict[str, Any]: 传感器数据字典
        """
        # 确保数值在有效范围内
        acc_x = np.clip(acc_x, -self.ACC_RANGE, self.ACC_RANGE)
        acc_y = np.clip(acc_y, -self.ACC_RANGE, self.ACC_RANGE)
        acc_z = np.clip(acc_z, -self.ACC_RANGE, self.ACC_RANGE)
        
        gyro_x = np.clip(gyro_x, -self.GYRO_RANGE, self.GYRO_RANGE)
        gyro_y = np.clip(gyro_y, -self.GYRO_RANGE, self.GYRO_RANGE)
        gyro_z = np.clip(gyro_z, -self.GYRO_RANGE, self.GYRO_RANGE)
        
        angle_x = np.clip(angle_x, -self.ANGLE_RANGE, self.ANGLE_RANGE)
        angle_y = np.clip(angle_y, -self.ANGLE_RANGE, self.ANGLE_RANGE)
        angle_z = np.clip(angle_z, -self.ANGLE_RANGE, self.ANGLE_RANGE)
        
        # 创建数据字典（符合JY901格式）
        return {
            '时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            '设备名称': self.sensor_id,
            '加速度X(g)': round(float(acc_x), 4),
            '加速度Y(g)': round(float(acc_y), 4),
            '加速度Z(g)': round(float(acc_z), 4),
            '角速度X(°/s)': round(float(gyro_x), 4),
            '角速度Y(°/s)': round(float(gyro_y), 4),
            '角速度Z(°/s)': round(float(gyro_z), 4),
            '角度X(°)': round(float(angle_x), 3),
            '角度Y(°)': round(float(angle_y), 3),
            '角度Z(°)': round(float(angle_z), 3),
            '温度(°C)': 25.0,
            '电量(%)': 100.0,
        }
