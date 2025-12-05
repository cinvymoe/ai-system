"""
JY901 九轴传感器采集器

支持从 JY901/JY901S 九轴传感器采集数据，包括：
- 加速度 (X, Y, Z)
- 角速度 (X, Y, Z)
- 角度 (X, Y, Z)
- 磁场 (X, Y, Z)
- 四元数
- 温度
- 电量
"""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, List, Callable, AsyncIterator
import threading
import time
import platform

try:
    import serial
    from serial import SerialException
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    print("警告: pyserial 未安装，实时模式不可用。请运行: pip install pyserial")

from .base import BaseSensorCollector
from ..models import CollectedData
from ..enums import CollectionStatus


class JY901Sensor(BaseSensorCollector):
    """JY901 九轴传感器采集器"""
    
    # 数据字段定义
    DATA_FIELDS = [
        '时间', '设备名称', '片上时间()', 
        '加速度X(g)', '加速度Y(g)', '加速度Z(g)',
        '角速度X(°/s)', '角速度Y(°/s)', '角速度Z(°/s)', 
        '角度X(°)', '角度Y(°)', '角度Z(°)',
        '磁场X(uT)', '磁场Y(uT)', '磁场Z(uT)', 
        '四元数0()', '四元数1()', '四元数2()', '四元数3()',
        '温度(°C)', '版本号()', '电量(%)'
    ]
    
    # 数值字段（需要转换为浮点数）
    NUMERIC_FIELDS = [
        '加速度X(g)', '加速度Y(g)', '加速度Z(g)',
        '角速度X(°/s)', '角速度Y(°/s)', '角速度Z(°/s)',
        '角度X(°)', '角度Y(°)', '角度Z(°)',
        '磁场X(uT)', '磁场Y(uT)', '磁场Z(uT)',
        '四元数0()', '四元数1()', '四元数2()', '四元数3()',
        '温度(°C)', '电量(%)'
    ]
    
    # 数据有效性范围
    VALUE_RANGES = {
        '加速度X(g)': (-16, 16),
        '加速度Y(g)': (-16, 16),
        '加速度Z(g)': (-16, 16),
        '角速度X(°/s)': (-2000, 2000),
        '角速度Y(°/s)': (-2000, 2000),
        '角速度Z(°/s)': (-2000, 2000),
        '角度X(°)': (-180, 180),
        '角度Y(°)': (-180, 180),
        '角度Z(°)': (-180, 180),
        '温度(°C)': (-40, 85),
        '电量(%)': (0, 100)
    }
    
    def __init__(
        self, 
        sensor_id: str,
        data_file_path: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        初始化 JY901 传感器采集器
        
        Args:
            sensor_id: 传感器唯一标识
            data_file_path: 本地数据文件路径（用于回放模式）
            config: 传感器配置参数
                - mode: 'realtime' 或 'playback'（默认 'playback'）
                - interval: 数据发送间隔（秒，默认 0.01，仅回放模式）
                - loop: 是否循环播放（默认 False，仅回放模式）
                - port: 串口名称（实时模式必需，如 '/dev/ttyUSB0' 或 'COM3'）
                - baudrate: 波特率（默认 9600）
                - timeout: 串口超时（秒，默认 0.5）
        """
        super().__init__(sensor_id, 'jy901', config)
        
        self.data_file_path = data_file_path
        self.mode = self.config.get('mode', 'realtime')
        self.interval = self.config.get('interval', 0.01)
        self.loop = self.config.get('loop', False)
        
        # 串口配置（实时模式）
        self.port = self.config.get('port', self._get_default_port())
        self.baudrate = self.config.get('baudrate', 9600)
        self.timeout = self.config.get('timeout', 0.5)
        
        # 数据存储
        self.data_list: List[Dict[str, Any]] = []
        self.current_index = 0
        
        # 线程控制
        self.is_running = False
        self.send_thread: Optional[threading.Thread] = None
        self.read_thread: Optional[threading.Thread] = None
        self.data_lock = threading.Lock()
        
        # 当前数据缓存
        self.current_data: Optional[Dict[str, Any]] = None
        
        # 串口对象（实时模式）
        self.serial_port = None
        
        # 协议解析器（实时模式）
        self.temp_bytes = []
        self.pack_size = 11
        self.gyro_range = 2000.0
        self.acc_range = 16.0
        self.angle_range = 180.0
    
    def _get_default_port(self) -> str:
        """获取默认串口名称"""
        system = platform.system().lower()
        if system == 'linux':
            return '/dev/ttyS10'
        elif system == 'windows':
            return 'COM3'
        elif system == 'darwin':  # macOS
            return '/dev/tty.usbserial'
        else:
            return '/dev/ttyUSB0'
    
    async def connect(self) -> bool:
        """连接到传感器或加载数据文件"""
        try:
            if self.mode == 'playback':
                if not self.data_file_path:
                    raise ValueError("回放模式需要指定 data_file_path")
                
                # 加载本地数据文件
                self._load_data_file()
                
                if not self.data_list:
                    raise ValueError(f"数据文件为空或加载失败: {self.data_file_path}")
                
                print(f"JY901 传感器 [{self.sensor_id}] 已加载 {len(self.data_list)} 条数据")
            
            elif self.mode == 'realtime':
                if not SERIAL_AVAILABLE:
                    raise ImportError("pyserial 未安装，无法使用实时模式")
                
                # 打开串口
                self._open_serial_port()
                
                if not self.serial_port or not self.serial_port.is_open:
                    raise ConnectionError(f"无法打开串口: {self.port}")
                
                print(f"JY901 传感器 [{self.sensor_id}] 已连接到 {self.port} (波特率: {self.baudrate})")
            
            else:
                raise ValueError(f"不支持的模式: {self.mode}")
            
            self._is_connected = True
            return True
            
        except Exception as e:
            print(f"连接 JY901 传感器失败: {e}")
            return False
    
    async def disconnect(self) -> None:
        """断开传感器连接"""
        self.is_running = False
        
        # 等待线程结束
        if self.send_thread and self.send_thread.is_alive():
            self.send_thread.join(timeout=1.0)
        
        if self.read_thread and self.read_thread.is_alive():
            self.read_thread.join(timeout=1.0)
        
        # 关闭串口
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            print(f"串口 {self.port} 已关闭")
        
        self._is_connected = False
        print(f"JY901 传感器 [{self.sensor_id}] 已断开")
    
    async def read_sensor_data(self) -> Dict[str, Any]:
        """
        读取传感器数据
        
        Returns:
            Dict[str, Any]: 传感器数据字典
        """
        if self.mode == 'playback':
            return await self._read_playback_data()
        elif self.mode == 'realtime':
            return await self._read_realtime_data()
        else:
            raise ValueError(f"不支持的模式: {self.mode}")
    
    async def collect_stream(self) -> AsyncIterator[CollectedData]:
        """
        采集数据流（实现 IDataSource 接口）
        
        Yields:
            CollectedData: 持续采集的数据
        """
        if not self._is_connected:
            await self.connect()
        
        while self._is_connected and self.is_running:
            try:
                raw_data = await self.read_sensor_data()
                
                yield CollectedData(
                    source_id=self.sensor_id,
                    data=raw_data,
                    metadata={
                        'sensor_type': self.sensor_type,
                        'sensor_id': self.sensor_id,
                        'collection_time': datetime.now().isoformat(),
                    },
                    timestamp=datetime.now(),
                    status=CollectionStatus.SUCCESS
                )
                
            except Exception as e:
                yield CollectedData(
                    source_id=self.sensor_id,
                    data={},
                    metadata={
                        'sensor_type': self.sensor_type,
                        'sensor_id': self.sensor_id,
                        'error': str(e),
                    },
                    timestamp=datetime.now(),
                    status=CollectionStatus.FAILED
                )
                break
    
    def get_source_id(self) -> str:
        """
        获取数据源唯一标识（实现 IDataSource 接口）
        
        Returns:
            str: 传感器ID
        """
        return self.sensor_id
    
    async def _read_playback_data(self) -> Dict[str, Any]:
        """从本地文件读取数据（回放模式）"""
        if not self.is_running:
            # 启动数据发送线程
            self.is_running = True
            self.send_thread = threading.Thread(
                target=self._data_sending_loop, 
                daemon=True
            )
            self.send_thread.start()
        
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
    
    async def _read_realtime_data(self) -> Dict[str, Any]:
        """从串口读取实时数据"""
        if not self.is_running:
            # 启动串口读取线程
            self.is_running = True
            self.read_thread = threading.Thread(
                target=self._serial_read_loop,
                daemon=True
            )
            self.read_thread.start()
        
        # 等待数据可用
        max_wait = 10  # 最多等待10秒
        wait_count = 0
        while self.current_data is None and wait_count < max_wait * 100:
            await asyncio.sleep(0.01)
            wait_count += 1
        
        if self.current_data is None:
            raise TimeoutError("等待串口数据超时")
        
        # 返回当前数据的副本
        with self.data_lock:
            data = self.current_data.copy() if self.current_data else {}
        
        return data
    
    def _load_data_file(self):
        """加载本地数据文件"""
        try:
            file_path = Path(self.data_file_path)
            
            if not file_path.exists():
                raise FileNotFoundError(f"数据文件不存在: {self.data_file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if not lines:
                raise ValueError("数据文件为空")
            
            # 第一行是表头
            headers = lines[0].strip().split('\t')
            
            # 解析数据行
            for i in range(1, len(lines)):
                line = lines[i].strip()
                if not line:
                    continue
                
                values = line.split('\t')
                
                # 创建数据字典
                data_dict = {}
                for j in range(min(len(headers), len(values))):
                    header = headers[j]
                    value = values[j]
                    
                    # 转换数值字段
                    if header in self.NUMERIC_FIELDS:
                        try:
                            data_dict[header] = float(value)
                        except (ValueError, TypeError):
                            data_dict[header] = None
                    else:
                        data_dict[header] = value
                
                # 验证数据有效性
                if self._validate_data(data_dict):
                    self.data_list.append(data_dict)
            
            print(f"成功加载 {len(self.data_list)} 条有效数据")
            
        except Exception as e:
            print(f"加载数据文件失败: {e}")
            raise
    
    def _validate_data(self, data: Dict[str, Any]) -> bool:
        """验证数据有效性"""
        try:
            # 检查必要字段
            required_fields = ['加速度X(g)', '加速度Y(g)', '加速度Z(g)']
            for field in required_fields:
                if field not in data or data[field] is None:
                    return False
            
            # 检查数值范围
            for field, (min_val, max_val) in self.VALUE_RANGES.items():
                if field in data and data[field] is not None:
                    value = data[field]
                    if not (min_val <= value <= max_val):
                        print(f"数据超出范围: {field}={value}")
                        return False
            
            return True
            
        except Exception:
            return False
    
    def _data_sending_loop(self):
        """数据发送循环（在独立线程中运行）"""
        while self.is_running:
            try:
                if self.current_index < len(self.data_list):
                    # 获取当前数据
                    data = self.data_list[self.current_index]
                    
                    # 更新当前数据缓存
                    with self.data_lock:
                        self.current_data = data
                    
                    # 更新索引
                    self.current_index += 1
                    
                    # 如果到达末尾
                    if self.current_index >= len(self.data_list):
                        if self.loop:
                            # 循环播放
                            self.current_index = 0
                            print(f"JY901 传感器 [{self.sensor_id}] 循环播放")
                        else:
                            # 停止播放
                            print(f"JY901 传感器 [{self.sensor_id}] 数据播放完毕")
                            self.is_running = False
                            break
                else:
                    # 没有数据
                    self.is_running = False
                    break
                
                # 等待指定间隔
                time.sleep(self.interval)
                
            except Exception as e:
                print(f"数据发送错误: {e}")
                time.sleep(self.interval)
    
    def get_acceleration(self) -> Optional[Dict[str, float]]:
        """获取加速度数据"""
        if self.current_data:
            return {
                'x': self.current_data.get('加速度X(g)'),
                'y': self.current_data.get('加速度Y(g)'),
                'z': self.current_data.get('加速度Z(g)')
            }
        return None
    
    def get_gyroscope(self) -> Optional[Dict[str, float]]:
        """获取角速度数据"""
        if self.current_data:
            return {
                'x': self.current_data.get('角速度X(°/s)'),
                'y': self.current_data.get('角速度Y(°/s)'),
                'z': self.current_data.get('角速度Z(°/s)')
            }
        return None
    
    def get_angle(self) -> Optional[Dict[str, float]]:
        """获取角度数据"""
        if self.current_data:
            return {
                'x': self.current_data.get('角度X(°)'),
                'y': self.current_data.get('角度Y(°)'),
                'z': self.current_data.get('角度Z(°)')
            }
        return None
    
    def get_magnetic(self) -> Optional[Dict[str, float]]:
        """获取磁场数据"""
        if self.current_data:
            return {
                'x': self.current_data.get('磁场X(uT)'),
                'y': self.current_data.get('磁场Y(uT)'),
                'z': self.current_data.get('磁场Z(uT)')
            }
        return None
    
    def get_quaternion(self) -> Optional[Dict[str, float]]:
        """获取四元数数据"""
        if self.current_data:
            return {
                'q0': self.current_data.get('四元数0()'),
                'q1': self.current_data.get('四元数1()'),
                'q2': self.current_data.get('四元数2()'),
                'q3': self.current_data.get('四元数3()')
            }
        return None
    
    def get_temperature(self) -> Optional[float]:
        """获取温度数据"""
        if self.current_data:
            return self.current_data.get('温度(°C)')
        return None
    
    def get_battery(self) -> Optional[float]:
        """获取电量数据"""
        if self.current_data:
            return self.current_data.get('电量(%)')
        return None
    
    def get_progress(self) -> Dict[str, Any]:
        """获取播放进度"""
        return {
            'current_index': self.current_index,
            'total_count': len(self.data_list),
            'progress': (self.current_index / len(self.data_list) * 100) if self.data_list else 0
        }
    
    # ==================== IDataSource 接口实现 ====================
    
    async def collect_stream(self) -> AsyncIterator[CollectedData]:
        """
        采集数据流（IDataSource 接口要求）
        
        Yields:
            CollectedData: 持续采集的数据
        """
        async for data in self.collect():
            yield data
    
    def get_source_id(self) -> str:
        """
        获取数据源唯一标识（IDataSource 接口要求）
        
        Returns:
            str: 传感器ID
        """
        return self.sensor_id
    
    # ==================== 串口通信方法（实时模式） ====================
    
    def _open_serial_port(self):
        """打开串口"""
        try:
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
            
            self.serial_port = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            
            print(f"串口已打开: {self.port} @ {self.baudrate} bps")
            
        except SerialException as e:
            print(f"打开串口失败: {self.port} @ {self.baudrate} - {e}")
            raise
    
    def _serial_read_loop(self):
        """串口读取循环（在独立线程中运行）"""
        print(f"串口读取线程已启动: {self.port}")
        
        while self.is_running:
            try:
                if self.serial_port and self.serial_port.is_open:
                    # 检查是否有数据可读
                    if self.serial_port.in_waiting > 0:
                        data = self.serial_port.read(self.serial_port.in_waiting)
                        self._parse_serial_data(data)
                else:
                    time.sleep(0.1)
                    break
                    
            except Exception as e:
                print(f"串口读取错误: {e}")
                time.sleep(0.1)
        
        print("串口读取线程已停止")
    
    def _parse_serial_data(self, data: bytes):
        """
        解析串口数据（WIT协议）
        
        数据包格式:
        - 包头: 0x55
        - 类型: 0x50-0x5A, 0x5F
        - 数据: 8字节
        - 校验和: 1字节
        """
        for byte in data:
            self.temp_bytes.append(byte)
            
            # 检查包头
            if self.temp_bytes[0] != 0x55:
                del self.temp_bytes[0]
                continue
            
            # 检查类型字节
            if len(self.temp_bytes) > 1:
                type_byte = self.temp_bytes[1]
                valid_types = list(range(0x50, 0x5B)) + [0x5F]
                if type_byte not in valid_types:
                    del self.temp_bytes[0]
                    continue
            
            # 完整数据包
            if len(self.temp_bytes) == self.pack_size:
                # 校验和
                checksum = sum(self.temp_bytes[:-1]) & 0xFF
                
                if checksum == self.temp_bytes[-1]:
                    # 解析数据包
                    self._process_data_packet(self.temp_bytes)
                else:
                    # 校验失败
                    del self.temp_bytes[0]
                
                # 清空缓冲区
                self.temp_bytes = []
    
    def _process_data_packet(self, packet: List[int]):
        """处理数据包"""
        packet_type = packet[1]
        
        with self.data_lock:
            if self.current_data is None:
                self.current_data = {}
            
            if packet_type == 0x50:  # 时间包
                self._parse_time_packet(packet)
            elif packet_type == 0x51:  # 加速度包
                self._parse_acc_packet(packet)
            elif packet_type == 0x52:  # 角速度包
                self._parse_gyro_packet(packet)
            elif packet_type == 0x53:  # 角度包
                self._parse_angle_packet(packet)
            elif packet_type == 0x54:  # 磁场包
                self._parse_mag_packet(packet)
            elif packet_type == 0x59:  # 四元数包
                self._parse_quaternion_packet(packet)
    
    def _parse_time_packet(self, packet: List[int]):
        """解析时间包"""
        # 提取时间信息
        year = 2000 + (packet[2])
        month = packet[3]
        day = packet[4]
        hour = packet[5]
        minute = packet[6]
        second = packet[7]
        millisecond = (packet[9] << 8) | packet[8]
        
        time_str = f"{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}.{millisecond:03d}"
        self.current_data['片上时间()'] = time_str
    
    def _parse_acc_packet(self, packet: List[int]):
        """解析加速度包"""
        # 提取加速度数据
        ax = self._bytes_to_int16([packet[2], packet[3]]) / 32768.0 * self.acc_range
        ay = self._bytes_to_int16([packet[4], packet[5]]) / 32768.0 * self.acc_range
        az = self._bytes_to_int16([packet[6], packet[7]]) / 32768.0 * self.acc_range
        
        # 提取温度
        temp = ((packet[9] << 8) | packet[8]) / 100.0
        
        self.current_data['加速度X(g)'] = round(ax, 4)
        self.current_data['加速度Y(g)'] = round(ay, 4)
        self.current_data['加速度Z(g)'] = round(az, 4)
        self.current_data['温度(°C)'] = round(temp, 2)
    
    def _parse_gyro_packet(self, packet: List[int]):
        """解析角速度包"""
        gx = self._bytes_to_int16([packet[2], packet[3]]) / 32768.0 * self.gyro_range
        gy = self._bytes_to_int16([packet[4], packet[5]]) / 32768.0 * self.gyro_range
        gz = self._bytes_to_int16([packet[6], packet[7]]) / 32768.0 * self.gyro_range
        
        self.current_data['角速度X(°/s)'] = round(gx, 4)
        self.current_data['角速度Y(°/s)'] = round(gy, 4)
        self.current_data['角速度Z(°/s)'] = round(gz, 4)
    
    def _parse_angle_packet(self, packet: List[int]):
        """解析角度包"""
        rx = self._bytes_to_int16([packet[2], packet[3]]) / 32768.0 * self.angle_range
        ry = self._bytes_to_int16([packet[4], packet[5]]) / 32768.0 * self.angle_range
        rz = self._bytes_to_int16([packet[6], packet[7]]) / 32768.0 * self.angle_range
        
        self.current_data['角度X(°)'] = round(rx, 3)
        self.current_data['角度Y(°)'] = round(ry, 3)
        self.current_data['角度Z(°)'] = round(rz, 3)
    
    def _parse_mag_packet(self, packet: List[int]):
        """解析磁场包"""
        mx = self._bytes_to_int16([packet[2], packet[3]])
        my = self._bytes_to_int16([packet[4], packet[5]])
        mz = self._bytes_to_int16([packet[6], packet[7]])
        
        self.current_data['磁场X(uT)'] = float(mx)
        self.current_data['磁场Y(uT)'] = float(my)
        self.current_data['磁场Z(uT)'] = float(mz)
    
    def _parse_quaternion_packet(self, packet: List[int]):
        """解析四元数包"""
        q0 = self._bytes_to_int16([packet[2], packet[3]]) / 32768.0
        q1 = self._bytes_to_int16([packet[4], packet[5]]) / 32768.0
        q2 = self._bytes_to_int16([packet[6], packet[7]]) / 32768.0
        q3 = self._bytes_to_int16([packet[8], packet[9]]) / 32768.0
        
        self.current_data['四元数0()'] = round(q0, 5)
        self.current_data['四元数1()'] = round(q1, 5)
        self.current_data['四元数2()'] = round(q2, 5)
        self.current_data['四元数3()'] = round(q3, 5)
    
    def _bytes_to_int16(self, bytes_list: List[int]) -> int:
        """将字节列表转换为有符号16位整数"""
        value = (bytes_list[1] << 8) | bytes_list[0]
        # 处理负数
        if value >= 32768:
            value -= 65536
        return value
    
    # ==================== 串口命令方法 ====================
    
    def write_register(self, reg_addr: int, value: int) -> bool:
        """
        写入寄存器
        
        Args:
            reg_addr: 寄存器地址
            value: 写入值
            
        Returns:
            bool: 是否成功
        """
        if not self.serial_port or not self.serial_port.is_open:
            print("串口未打开")
            return False
        
        try:
            cmd = bytes([0xFF, 0xAA, reg_addr, value & 0xFF, value >> 8])
            self.serial_port.write(cmd)
            return True
        except Exception as e:
            print(f"写入寄存器失败: {e}")
            return False
    
    def unlock(self) -> bool:
        """解锁传感器配置"""
        return self.write_register(0x69, 0xB588)
    
    def save_config(self) -> bool:
        """保存配置到传感器"""
        return self.write_register(0x00, 0x00)
    
    def calibrate_acceleration(self) -> bool:
        """
        加速度校准
        注意: 传感器需要水平放置且静止
        """
        if not self.unlock():
            return False
        
        time.sleep(0.1)
        
        if not self.write_register(0x01, 0x01):
            return False
        
        print("加速度校准中，请保持传感器水平静止...")
        time.sleep(5.5)
        print("加速度校准完成")
        
        return True
    
    def start_magnetic_calibration(self) -> bool:
        """
        开始磁场校准
        注意: 需要在8字形晃动传感器
        """
        if not self.unlock():
            return False
        
        time.sleep(0.1)
        
        if not self.write_register(0x01, 0x07):
            return False
        
        print("磁场校准已开始，请以8字形晃动传感器...")
        return True
    
    def end_magnetic_calibration(self) -> bool:
        """结束磁场校准并保存"""
        if not self.unlock():
            return False
        
        time.sleep(0.1)
        
        if not self.save_config():
            return False
        
        print("磁场校准已完成并保存")
        return True
