"""
Motion Direction Processor

数据处理层，分析传感器数据并输出运动方向指令。
使用 MotionDirectionCalculator 进行运动分析。
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

from datahandler.algorithms.MotionDirectionCalculator import MotionDirectionCalculator
from ..models import MotionCommand


# 配置日志
logger = logging.getLogger(__name__)


class MotionDirectionProcessor:
    """
    运动方向处理器
    
    接收传感器数据，使用 MotionDirectionCalculator 分析数据，
    输出标准化的运动指令。
    """
    
    # 方向字符串映射到标准化命令
    DIRECTION_MAPPING = {
        '东': 'forward',
        '西': 'backward',
        '南': 'turn_left',
        '北': 'turn_right',
        '静止': 'stationary',
        '微弱运动': 'stationary',
    }
    
    # 旋转字符串映射
    ROTATION_MAPPING = {
        '绕Z轴正转': 'turn_right',
        '绕Z轴反转': 'turn_left',
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化运动方向处理器
        
        Args:
            config: 配置参数（可选）
                - motion_threshold: 运动检测阈值 (g)
                - angular_threshold: 角速度检测阈值 (度/秒)
                - direction_threshold: 方向判断阈值 (g)
                - rotation_threshold: 旋转检测阈值 (度/秒)
                - velocity_threshold: 速度判断阈值 (m/s)
        """
        self.config = config or {}
        
        # 初始化 MotionDirectionCalculator
        self.calculator = MotionDirectionCalculator(
            motion_threshold=self.config.get('motion_threshold', 0.005),
            angular_threshold=self.config.get('angular_threshold', 2.0),
            direction_threshold=self.config.get('direction_threshold', 0.002),
            rotation_threshold=self.config.get('rotation_threshold', 5.0),
            velocity_threshold=self.config.get('velocity_threshold', 0.0005),
        )
        
        # 运动状态跟踪
        self.last_motion_state = {
            'is_moving': False,
            'direction': 'stationary',
            'last_update': None,
        }
        
        logger.info("MotionDirectionProcessor 已初始化")
    
    def process(self, sensor_data: Dict[str, Any]) -> MotionCommand:
        """
        处理传感器数据并生成运动指令
        
        Args:
            sensor_data: 传感器数据字典，包含加速度、角速度和角度信息
            
        Returns:
            MotionCommand: 运动指令对象
        """
        try:
            # 提取传感器数据字段
            acceleration = self._extract_acceleration(sensor_data)
            angular_velocity = self._extract_angular_velocity(sensor_data)
            angles = self._extract_angles(sensor_data)
            
            # 记录原始传感器值
            logger.debug(
                f"原始传感器数据 - 加速度: {acceleration}, "
                f"角速度: {angular_velocity}, 角度: {angles}"
            )
            
            # 调用 MotionDirectionCalculator 计算运动方向
            direction_info = self.calculator.calculate_motion_direction(
                acceleration=acceleration,
                angles=angles,
                angular_velocity=angular_velocity,
                timestamp=None  # 使用系统时间
            )
            
            # 提取主要运动方向
            primary_direction = direction_info.get('direction', '静止')
            rotation = direction_info.get('rotation', '静止')
            intensity = direction_info.get('intensity', 0.0)
            angular_intensity = direction_info.get('angular_intensity', 0.0)
            
            # 检测运动开始事件
            is_motion_start = bool(direction_info.get('motion_start', False))
            
            # 映射方向字符串到标准化命令
            command = self._map_direction_to_command(primary_direction, rotation)
            
            # 创建 MotionCommand 对象
            motion_command = MotionCommand(
                command=command,
                intensity=float(intensity),
                angular_intensity=float(angular_intensity),
                timestamp=datetime.now(),
                is_motion_start=is_motion_start,
                raw_direction=str(primary_direction),
                metadata={
                    'rotation': rotation,
                    'velocity': direction_info.get('velocity', {}),
                    'components': direction_info.get('components', {}),
                    'is_moving': direction_info.get('is_moving', False),
                }
            )
            
            # 记录计算结果
            logger.info(
                f"运动指令 - 命令: {command}, 强度: {intensity:.4f}, "
                f"角强度: {angular_intensity:.4f}, 运动开始: {is_motion_start}"
            )
            
            # 更新运动状态
            self._update_motion_state(motion_command)
            
            return motion_command
            
        except KeyError as e:
            # 缺少必需的传感器数据字段
            logger.error(f"传感器数据缺少必需字段: {e}")
            return self._create_error_command(
                f"缺少必需字段: {e}",
                sensor_data
            )
        except ValueError as e:
            # 无效的数据类型
            logger.error(f"传感器数据类型无效: {e}")
            return self._create_error_command(
                f"数据类型无效: {e}",
                sensor_data
            )
        except Exception as e:
            # MotionDirectionCalculator 异常或其他错误
            logger.error(f"处理传感器数据时发生错误: {e}", exc_info=True)
            return self._create_error_command(
                f"处理错误: {e}",
                sensor_data
            )
    
    def _extract_acceleration(self, sensor_data: Dict[str, Any]) -> list:
        """
        从传感器数据中提取加速度
        
        Args:
            sensor_data: 传感器数据字典
            
        Returns:
            list: [accX, accY, accZ]
            
        Raises:
            KeyError: 缺少必需字段
            ValueError: 数据类型无效
        """
        try:
            acc_x = float(sensor_data['加速度X(g)'])
            acc_y = float(sensor_data['加速度Y(g)'])
            acc_z = float(sensor_data['加速度Z(g)'])
            return [acc_x, acc_y, acc_z]
        except KeyError as e:
            raise KeyError(f"加速度字段 {e}")
        except (TypeError, ValueError) as e:
            raise ValueError(f"加速度数据转换失败: {e}")
    
    def _extract_angular_velocity(self, sensor_data: Dict[str, Any]) -> list:
        """
        从传感器数据中提取角速度
        
        Args:
            sensor_data: 传感器数据字典
            
        Returns:
            list: [gyroX, gyroY, gyroZ]
            
        Raises:
            KeyError: 缺少必需字段
            ValueError: 数据类型无效
        """
        try:
            gyro_x = float(sensor_data['角速度X(°/s)'])
            gyro_y = float(sensor_data['角速度Y(°/s)'])
            gyro_z = float(sensor_data['角速度Z(°/s)'])
            return [gyro_x, gyro_y, gyro_z]
        except KeyError as e:
            raise KeyError(f"角速度字段 {e}")
        except (TypeError, ValueError) as e:
            raise ValueError(f"角速度数据转换失败: {e}")
    
    def _extract_angles(self, sensor_data: Dict[str, Any]) -> list:
        """
        从传感器数据中提取角度
        
        Args:
            sensor_data: 传感器数据字典
            
        Returns:
            list: [angleX, angleY, angleZ]
            
        Raises:
            KeyError: 缺少必需字段
            ValueError: 数据类型无效
        """
        try:
            angle_x = float(sensor_data['角度X(°)'])
            angle_y = float(sensor_data['角度Y(°)'])
            angle_z = float(sensor_data['角度Z(°)'])
            return [angle_x, angle_y, angle_z]
        except KeyError as e:
            raise KeyError(f"角度字段 {e}")
        except (TypeError, ValueError) as e:
            raise ValueError(f"角度数据转换失败: {e}")
    
    def _map_direction_to_command(self, direction: str, rotation: str) -> str:
        """
        将方向字符串映射到标准化运动命令
        
        Args:
            direction: 主要运动方向字符串
            rotation: 旋转方向字符串
            
        Returns:
            str: 标准化命令 ('forward', 'backward', 'turn_left', 'turn_right', 'stationary')
        """
        # 首先检查旋转（旋转优先级高于线性运动）
        if rotation != '静止' and rotation != '无明显旋转':
            # 检查是否包含Z轴旋转
            if '绕Z轴正转' in rotation:
                return 'turn_right'
            elif '绕Z轴反转' in rotation:
                return 'turn_left'
        
        # 然后检查线性运动方向
        for key, command in self.DIRECTION_MAPPING.items():
            if key in direction:
                return command
        
        # 默认返回静止
        return 'stationary'
    
    def _update_motion_state(self, motion_command: MotionCommand) -> None:
        """
        更新运动状态跟踪
        
        Args:
            motion_command: 运动指令对象
        """
        self.last_motion_state = {
            'is_moving': motion_command.metadata.get('is_moving', False),
            'direction': motion_command.command,
            'last_update': motion_command.timestamp,
        }
    
    def _create_error_command(
        self,
        error_message: str,
        sensor_data: Dict[str, Any]
    ) -> MotionCommand:
        """
        创建错误情况下的静止命令
        
        Args:
            error_message: 错误消息
            sensor_data: 原始传感器数据
            
        Returns:
            MotionCommand: 静止命令，包含错误信息
        """
        return MotionCommand(
            command='stationary',
            intensity=0.0,
            angular_intensity=0.0,
            timestamp=datetime.now(),
            is_motion_start=False,
            raw_direction='错误',
            metadata={
                'error': error_message,
                'sensor_data': sensor_data,
            }
        )
    
    def get_motion_state(self) -> Dict[str, Any]:
        """
        获取当前运动状态
        
        Returns:
            Dict[str, Any]: 运动状态信息
        """
        return self.last_motion_state.copy()
    
    def reset(self) -> None:
        """
        重置处理器状态
        """
        self.calculator.reset_velocity()
        self.last_motion_state = {
            'is_moving': False,
            'direction': 'stationary',
            'last_update': None,
        }
        logger.info("MotionDirectionProcessor 已重置")
