"""Cross-Cutting Interfaces for Error Handling, Events, and Task Tracking."""

from abc import ABC, abstractmethod
from typing import Callable

from ..models import (
    ErrorInfo,
    ErrorType,
    SystemEvent,
    EventType,
    TaskInfo,
    TaskStatus,
)


class IErrorHandler(ABC):
    """错误处理器接口
    
    用于处理系统中发生的各类错误。
    实现此接口可以自定义错误处理逻辑。
    """
    
    @abstractmethod
    async def handle_error(self, error: ErrorInfo) -> None:
        """处理错误
        
        接收错误信息并执行相应的处理逻辑，如记录日志、发送告警等。
        
        Args:
            error: 错误信息，包含错误类型、时间戳、层名称、操作、消息和详细信息
            
        Raises:
            RuntimeError: 当错误处理本身失败时
        """
        pass
    
    @abstractmethod
    def can_handle(self, error_type: ErrorType) -> bool:
        """判断是否可以处理该类型错误
        
        Args:
            error_type: 错误类型（CONFIGURATION、CONNECTION、VALIDATION、PROCESSING、STORAGE）
            
        Returns:
            bool: 如果可以处理该类型错误返回True，否则返回False
        """
        pass


class IEventEmitter(ABC):
    """事件发射器接口
    
    用于发布和订阅系统事件。
    支持事件驱动的架构模式。
    """
    
    @abstractmethod
    async def emit(self, event: SystemEvent) -> None:
        """发射事件
        
        向所有订阅了该事件类型的处理器发送事件。
        
        Args:
            event: 系统事件，包含事件类型、时间戳、来源和数据
            
        Raises:
            ValueError: 当事件无效时
            RuntimeError: 当事件发射失败时
        """
        pass
    
    @abstractmethod
    async def subscribe(self, event_type: EventType, handler: Callable) -> str:
        """订阅事件
        
        注册一个事件处理器，当指定类型的事件发生时会被调用。
        
        Args:
            event_type: 要订阅的事件类型（COLLECTION_START、COLLECTION_COMPLETE等）
            handler: 事件处理函数，接收SystemEvent作为参数
            
        Returns:
            str: 订阅ID，用于后续取消订阅
            
        Raises:
            ValueError: 当事件类型无效或处理器不可调用时
        """
        pass
    
    @abstractmethod
    async def unsubscribe(self, subscription_id: str) -> None:
        """取消订阅
        
        移除之前注册的事件处理器。
        
        Args:
            subscription_id: 订阅ID
            
        Raises:
            KeyError: 当订阅ID不存在时
        """
        pass


class ITaskTracker(ABC):
    """任务跟踪器接口
    
    用于跟踪异步操作的状态和进度。
    提供任务生命周期管理功能。
    """
    
    @abstractmethod
    async def create_task(self, task_type: str) -> str:
        """创建任务
        
        创建一个新的任务记录，用于跟踪异步操作。
        
        Args:
            task_type: 任务类型标识（如"collection"、"processing"、"storage"）
            
        Returns:
            str: 任务ID，用于后续操作
            
        Raises:
            ValueError: 当任务类型无效时
        """
        pass
    
    @abstractmethod
    async def update_status(self, task_id: str, status: TaskStatus) -> None:
        """更新任务状态
        
        更新任务的执行状态。
        
        Args:
            task_id: 任务ID
            status: 新的任务状态（PENDING、RUNNING、COMPLETED、FAILED、CANCELLED）
            
        Raises:
            KeyError: 当任务ID不存在时
            ValueError: 当状态转换无效时
        """
        pass
    
    @abstractmethod
    async def update_progress(self, task_id: str, progress: float) -> None:
        """更新任务进度
        
        更新任务的完成进度百分比。
        
        Args:
            task_id: 任务ID
            progress: 进度值，范围0.0到1.0
            
        Raises:
            KeyError: 当任务ID不存在时
            ValueError: 当进度值超出范围时
        """
        pass
    
    @abstractmethod
    async def get_task_info(self, task_id: str) -> TaskInfo:
        """获取任务信息
        
        检索任务的完整信息。
        
        Args:
            task_id: 任务ID
            
        Returns:
            TaskInfo: 任务信息，包含任务ID、类型、状态、时间戳、进度、结果和错误
            
        Raises:
            KeyError: 当任务ID不存在时
        """
        pass
    
    @abstractmethod
    async def cancel_task(self, task_id: str) -> None:
        """取消任务
        
        尝试取消正在执行或等待执行的任务。
        
        Args:
            task_id: 任务ID
            
        Raises:
            KeyError: 当任务ID不存在时
            RuntimeError: 当任务无法取消时（如已完成）
        """
        pass
