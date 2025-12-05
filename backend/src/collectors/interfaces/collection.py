"""Data Collection Layer Interfaces."""

from abc import ABC, abstractmethod
from typing import AsyncIterator, Dict, Any

from ..models import (
    CollectedData,
    ParsedMetadata,
    CollectionTask,
    CollectionStatistics,
)
from ..enums import CollectionStatus


class IDataSource(ABC):
    """数据源接口
    
    所有具体数据源必须实现此接口。
    """
    
    @abstractmethod
    async def connect(self) -> None:
        """建立与数据源的连接
        
        Raises:
            ConnectionError: 当连接失败时
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """断开与数据源的连接
        
        Raises:
            ConnectionError: 当断开连接失败时
        """
        pass
    
    @abstractmethod
    async def collect(self) -> CollectedData:
        """采集单次数据
        
        Returns:
            CollectedData: 采集到的数据及元数据
            
        Raises:
            ConnectionError: 当数据源未连接时
            ValueError: 当采集的数据无效时
        """
        pass
    
    @abstractmethod
    async def collect_stream(self) -> AsyncIterator[CollectedData]:
        """采集数据流
        
        Yields:
            CollectedData: 持续采集的数据及元数据
            
        Raises:
            ConnectionError: 当数据源未连接时
            ValueError: 当采集的数据无效时
        """
        pass
    
    @abstractmethod
    def get_source_id(self) -> str:
        """获取数据源唯一标识
        
        Returns:
            str: 数据源的唯一标识符
        """
        pass


class IMetadataParser(ABC):
    """元数据解析器接口
    
    用于从采集数据中提取和验证元数据。
    """
    
    @abstractmethod
    async def parse(self, collected_data: CollectedData) -> ParsedMetadata:
        """解析元数据
        
        Args:
            collected_data: 采集到的原始数据
            
        Returns:
            ParsedMetadata: 解析后的元数据
            
        Raises:
            ValueError: 当数据格式无效时
        """
        pass
    
    @abstractmethod
    async def validate(self, metadata: ParsedMetadata) -> bool:
        """验证元数据完整性和正确性
        
        Args:
            metadata: 解析后的元数据
            
        Returns:
            bool: 元数据是否有效
        """
        pass


class ICollectionManager(ABC):
    """采集管理器接口
    
    负责管理数据源的注册和采集任务。
    """
    
    @abstractmethod
    async def register_source(self, source: IDataSource, config: Dict[str, Any]) -> str:
        """注册数据源
        
        Args:
            source: 数据源实例
            config: 数据源配置
            
        Returns:
            str: 注册后的源ID
            
        Raises:
            ValueError: 当配置无效时
        """
        pass
    
    @abstractmethod
    async def unregister_source(self, source_id: str) -> None:
        """注销数据源
        
        Args:
            source_id: 数据源ID
            
        Raises:
            KeyError: 当源ID不存在时
        """
        pass
    
    @abstractmethod
    async def start_collection(self, source_id: str) -> str:
        """启动采集任务
        
        Args:
            source_id: 数据源ID
            
        Returns:
            str: 任务ID
            
        Raises:
            KeyError: 当源ID不存在时
            RuntimeError: 当任务已在运行时
        """
        pass
    
    @abstractmethod
    async def stop_collection(self, task_id: str) -> None:
        """停止采集任务
        
        Args:
            task_id: 任务ID
            
        Raises:
            KeyError: 当任务ID不存在时
        """
        pass
    
    @abstractmethod
    async def get_task_status(self, task_id: str) -> CollectionStatus:
        """获取任务状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            CollectionStatus: 任务当前状态
            
        Raises:
            KeyError: 当任务ID不存在时
        """
        pass
    
    @abstractmethod
    async def get_statistics(self, source_id: str) -> CollectionStatistics:
        """获取采集统计信息
        
        Args:
            source_id: 数据源ID
            
        Returns:
            CollectionStatistics: 采集统计信息
            
        Raises:
            KeyError: 当源ID不存在时
        """
        pass
