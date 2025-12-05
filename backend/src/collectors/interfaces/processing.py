"""Data Processing Layer Interfaces."""

from abc import ABC, abstractmethod
from typing import Any

from ..models import (
    ProcessingResult,
    PipelineStep,
    PipelineResult,
    ProcessingStatistics,
)


class IProcessor(ABC):
    """数据处理器接口
    
    定义单个处理步骤的抽象接口。
    所有具体处理器必须实现此接口。
    """
    
    @abstractmethod
    async def process(self, data: Any) -> ProcessingResult:
        """处理数据
        
        Args:
            data: 输入数据
            
        Returns:
            ProcessingResult: 处理结果，包含成功状态、处理后的数据或错误信息
            
        Raises:
            ValueError: 当输入数据无效时
        """
        pass
    
    @abstractmethod
    def get_processor_name(self) -> str:
        """获取处理器名称
        
        Returns:
            str: 处理器的唯一名称标识
        """
        pass
    
    @abstractmethod
    def validate_input(self, data: Any) -> bool:
        """验证输入数据
        
        Args:
            data: 待验证的输入数据
            
        Returns:
            bool: 输入数据是否有效
        """
        pass


class IPipeline(ABC):
    """处理管道接口
    
    定义多个处理步骤组合的抽象接口。
    管道按顺序执行多个处理器。
    """
    
    @abstractmethod
    async def add_step(self, processor: IProcessor, order: int) -> str:
        """添加处理步骤
        
        Args:
            processor: 处理器实例
            order: 执行顺序（数字越小越先执行）
            
        Returns:
            str: 步骤ID
            
        Raises:
            ValueError: 当处理器无效或顺序冲突时
        """
        pass
    
    @abstractmethod
    async def remove_step(self, step_id: str) -> None:
        """移除处理步骤
        
        Args:
            step_id: 步骤ID
            
        Raises:
            KeyError: 当步骤ID不存在时
        """
        pass
    
    @abstractmethod
    async def execute(self, input_data: Any) -> PipelineResult:
        """执行管道
        
        按顺序执行所有处理步骤，将前一步的输出作为下一步的输入。
        
        Args:
            input_data: 管道的初始输入数据
            
        Returns:
            PipelineResult: 管道执行结果，包含最终数据、各步骤结果和失败信息
        """
        pass
    
    @abstractmethod
    def get_steps(self) -> list[PipelineStep]:
        """获取所有步骤
        
        Returns:
            list[PipelineStep]: 按执行顺序排列的所有管道步骤
        """
        pass


class IProcessingManager(ABC):
    """处理管理器接口
    
    负责管理处理器和处理管道的生命周期。
    """
    
    @abstractmethod
    async def register_processor(self, processor: IProcessor) -> str:
        """注册处理器
        
        Args:
            processor: 处理器实例
            
        Returns:
            str: 处理器ID
            
        Raises:
            ValueError: 当处理器无效或已存在时
        """
        pass
    
    @abstractmethod
    async def unregister_processor(self, processor_id: str) -> None:
        """注销处理器
        
        Args:
            processor_id: 处理器ID
            
        Raises:
            KeyError: 当处理器ID不存在时
        """
        pass
    
    @abstractmethod
    async def create_pipeline(self, pipeline_id: str) -> IPipeline:
        """创建处理管道
        
        Args:
            pipeline_id: 管道ID
            
        Returns:
            IPipeline: 新创建的管道实例
            
        Raises:
            ValueError: 当管道ID已存在时
        """
        pass
    
    @abstractmethod
    async def get_pipeline(self, pipeline_id: str) -> IPipeline:
        """获取处理管道
        
        Args:
            pipeline_id: 管道ID
            
        Returns:
            IPipeline: 管道实例
            
        Raises:
            KeyError: 当管道ID不存在时
        """
        pass
    
    @abstractmethod
    async def delete_pipeline(self, pipeline_id: str) -> None:
        """删除处理管道
        
        Args:
            pipeline_id: 管道ID
            
        Raises:
            KeyError: 当管道ID不存在时
        """
        pass
    
    @abstractmethod
    async def get_statistics(self, pipeline_id: str) -> list[ProcessingStatistics]:
        """获取处理统计信息
        
        Args:
            pipeline_id: 管道ID
            
        Returns:
            list[ProcessingStatistics]: 管道中每个步骤的统计信息
            
        Raises:
            KeyError: 当管道ID不存在时
        """
        pass
