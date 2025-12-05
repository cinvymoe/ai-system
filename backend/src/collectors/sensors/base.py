"""
传感器采集器基类

提供传感器数据采集的基础实现。
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional, AsyncIterator

from ..interfaces import IDataSource
from ..models import CollectedData
from ..enums import CollectionStatus


class BaseSensorCollector(IDataSource, ABC):
    """传感器采集器基类"""
    
    def __init__(self, sensor_id: str, sensor_type: str, config: Optional[Dict[str, Any]] = None):
        """
        初始化传感器采集器
        
        Args:
            sensor_id: 传感器唯一标识
            sensor_type: 传感器类型
            config: 传感器配置参数
        """
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type
        self.config = config or {}
        self._is_connected = False
    
    @abstractmethod
    async def connect(self) -> bool:
        """
        连接到传感器
        
        Returns:
            bool: 连接是否成功
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """断开传感器连接"""
        pass
    
    @abstractmethod
    async def read_sensor_data(self) -> Dict[str, Any]:
        """
        读取传感器原始数据
        
        Returns:
            Dict[str, Any]: 传感器原始数据
        """
        pass
    
    async def collect(self) -> AsyncIterator[CollectedData]:
        """
        采集传感器数据
        
        Yields:
            CollectedData: 采集到的数据
        """
        if not self._is_connected:
            await self.connect()
        
        try:
            raw_data = await self.read_sensor_data()
            
            collected_data = CollectedData(
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
            
            yield collected_data
            
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
    
    async def validate(self) -> bool:
        """
        验证传感器连接和配置
        
        Returns:
            bool: 验证是否通过
        """
        try:
            return await self.connect()
        except Exception:
            return False
    
    async def cleanup(self) -> None:
        """清理资源"""
        if self._is_connected:
            await self.disconnect()
