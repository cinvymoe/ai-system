"""Data Storage Layer Interfaces."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from ..models import (
    StorageLocation,
    QueryCriteria,
    StorageStatistics,
)


class IStorageBackend(ABC):
    """存储后端接口
    
    定义数据持久化操作的抽象接口。
    所有具体存储后端必须实现此接口。
    """
    
    @abstractmethod
    async def connect(self) -> None:
        """连接到存储后端
        
        建立与存储系统的连接，初始化必要的资源。
        
        Raises:
            ConnectionError: 当连接失败时
            ValueError: 当配置无效时
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """断开存储后端连接
        
        关闭与存储系统的连接，释放资源。
        
        Raises:
            ConnectionError: 当断开连接失败时
        """
        pass
    
    @abstractmethod
    async def store(self, data: Any) -> StorageLocation:
        """存储数据
        
        将处理后的数据持久化到存储系统。
        
        Args:
            data: 要存储的数据
            
        Returns:
            StorageLocation: 存储位置信息，包含backend_id、location_id、path和created_at
            
        Raises:
            ConnectionError: 当存储后端未连接时
            ValueError: 当数据格式无效时
            RuntimeError: 当存储操作失败时
        """
        pass
    
    @abstractmethod
    async def query(self, criteria: QueryCriteria) -> List[Any]:
        """查询数据
        
        根据查询条件从存储系统检索数据。
        
        Args:
            criteria: 查询条件，包含filters、sort_by、limit和offset
            
        Returns:
            List[Any]: 符合条件的数据列表
            
        Raises:
            ConnectionError: 当存储后端未连接时
            ValueError: 当查询条件无效时
        """
        pass
    
    @abstractmethod
    async def delete(self, location_id: str) -> None:
        """删除数据
        
        从存储系统中删除指定位置的数据。
        
        Args:
            location_id: 存储位置标识符
            
        Raises:
            ConnectionError: 当存储后端未连接时
            KeyError: 当location_id不存在时
            RuntimeError: 当删除操作失败时
        """
        pass
    
    @abstractmethod
    def get_backend_id(self) -> str:
        """获取后端ID
        
        返回存储后端的唯一标识符。
        
        Returns:
            str: 存储后端的唯一标识符
        """
        pass


class IStorageManager(ABC):
    """存储管理器接口
    
    负责管理存储后端和存储操作的协调。
    提供统一的存储访问接口，支持多个存储后端。
    """
    
    @abstractmethod
    async def register_backend(self, backend: IStorageBackend, config: Dict[str, Any]) -> str:
        """注册存储后端
        
        将存储后端注册到管理器，验证配置并初始化后端。
        
        Args:
            backend: 存储后端实例
            config: 存储后端配置
            
        Returns:
            str: 注册后的后端ID
            
        Raises:
            ValueError: 当配置无效时
            RuntimeError: 当后端已存在时
        """
        pass
    
    @abstractmethod
    async def unregister_backend(self, backend_id: str) -> None:
        """注销存储后端
        
        从管理器中移除存储后端，断开连接并清理资源。
        
        Args:
            backend_id: 存储后端ID
            
        Raises:
            KeyError: 当backend_id不存在时
            RuntimeError: 当后端正在使用时
        """
        pass
    
    @abstractmethod
    async def store_data(self, backend_id: str, data: Any) -> StorageLocation:
        """存储数据到指定后端
        
        将数据存储到指定的存储后端。
        
        Args:
            backend_id: 目标存储后端ID
            data: 要存储的数据
            
        Returns:
            StorageLocation: 存储位置信息
            
        Raises:
            KeyError: 当backend_id不存在时
            ConnectionError: 当存储后端未连接时
            ValueError: 当数据格式无效时
            RuntimeError: 当存储操作失败时
        """
        pass
    
    @abstractmethod
    async def query_data(self, backend_id: str, criteria: QueryCriteria) -> List[Any]:
        """从指定后端查询数据
        
        从指定的存储后端检索数据。
        
        Args:
            backend_id: 目标存储后端ID
            criteria: 查询条件
            
        Returns:
            List[Any]: 符合条件的数据列表
            
        Raises:
            KeyError: 当backend_id不存在时
            ConnectionError: 当存储后端未连接时
            ValueError: 当查询条件无效时
        """
        pass
    
    @abstractmethod
    async def get_statistics(self, backend_id: str) -> StorageStatistics:
        """获取存储统计信息
        
        获取指定存储后端的统计信息。
        
        Args:
            backend_id: 存储后端ID
            
        Returns:
            StorageStatistics: 存储统计信息，包含backend_id、stored_count、
                             storage_usage_bytes和last_storage_time
            
        Raises:
            KeyError: 当backend_id不存在时
        """
        pass
