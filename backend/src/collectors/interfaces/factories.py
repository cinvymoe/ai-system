"""Factory Interfaces for Data Collector Module.

工厂接口用于创建各层的实例，遵循依赖倒置原则。
"""

from abc import ABC, abstractmethod

from .collection import ICollectionManager, IMetadataParser
from .processing import IProcessingManager, IPipeline
from .storage import IStorageManager


class ICollectionLayerFactory(ABC):
    """采集层工厂接口
    
    用于创建数据采集层的各种组件实例。
    实现此接口以提供具体的采集层组件创建逻辑。
    """
    
    @abstractmethod
    def create_collection_manager(self) -> ICollectionManager:
        """创建采集管理器
        
        创建并返回一个采集管理器实例，用于管理数据源和采集任务。
        
        Returns:
            ICollectionManager: 采集管理器实例
            
        Raises:
            RuntimeError: 当创建失败时
        """
        pass
    
    @abstractmethod
    def create_metadata_parser(self) -> IMetadataParser:
        """创建元数据解析器
        
        创建并返回一个元数据解析器实例，用于解析和验证采集数据的元数据。
        
        Returns:
            IMetadataParser: 元数据解析器实例
            
        Raises:
            RuntimeError: 当创建失败时
        """
        pass


class IProcessingLayerFactory(ABC):
    """处理层工厂接口
    
    用于创建数据处理层的各种组件实例。
    实现此接口以提供具体的处理层组件创建逻辑。
    """
    
    @abstractmethod
    def create_processing_manager(self) -> IProcessingManager:
        """创建处理管理器
        
        创建并返回一个处理管理器实例，用于管理处理器和处理管道。
        
        Returns:
            IProcessingManager: 处理管理器实例
            
        Raises:
            RuntimeError: 当创建失败时
        """
        pass
    
    @abstractmethod
    def create_pipeline(self) -> IPipeline:
        """创建处理管道
        
        创建并返回一个新的处理管道实例。
        
        Returns:
            IPipeline: 处理管道实例
            
        Raises:
            RuntimeError: 当创建失败时
        """
        pass


class IStorageLayerFactory(ABC):
    """存储层工厂接口
    
    用于创建数据存储层的各种组件实例。
    实现此接口以提供具体的存储层组件创建逻辑。
    """
    
    @abstractmethod
    def create_storage_manager(self) -> IStorageManager:
        """创建存储管理器
        
        创建并返回一个存储管理器实例，用于管理存储后端和存储操作。
        
        Returns:
            IStorageManager: 存储管理器实例
            
        Raises:
            RuntimeError: 当创建失败时
        """
        pass
