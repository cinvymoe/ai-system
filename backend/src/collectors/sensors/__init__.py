"""
传感器数据采集模块

该模块提供各种传感器的数据采集功能。
"""

from .base import BaseSensorCollector
from .jy901 import JY901Sensor

__all__ = [
    'BaseSensorCollector',
    'JY901Sensor',
]
