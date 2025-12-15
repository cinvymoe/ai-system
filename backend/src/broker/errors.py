"""
Custom exceptions for the Message Broker module.
"""

import logging
import time
from typing import Any, Callable, Optional
from .models import MessageData, ValidationResult


class BrokerError(Exception):
    """消息代理基础异常"""
    pass


class ValidationError(BrokerError):
    """数据验证异常"""
    pass


class SubscriptionError(BrokerError):
    """订阅相关异常"""
    pass


class PublishError(BrokerError):
    """消息发布异常"""
    pass


class MessageTypeError(BrokerError):
    """消息类型相关异常"""
    pass


class CameraMappingError(BrokerError):
    """摄像头映射异常"""
    pass


class DatabaseError(BrokerError):
    """数据库操作异常"""
    pass


class ErrorHandler:
    """
    错误处理器
    
    负责处理消息代理中的各类错误：
    - 验证错误：拒绝消息，记录日志
    - 数据库错误：重试机制，降级处理
    - 订阅者错误：隔离错误，不影响其他订阅者
    
    实现要求：
    - Requirements 2.4: 处理发布失败
    - Requirements 3.5: 处理无效角度数据
    - Requirements 8.3: 记录错误日志
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        初始化错误处理器
        
        Args:
            logger: 日志记录器，如果不提供则创建新的
        """
        self._logger = logger or logging.getLogger(__name__)
        self._cache: dict = {}  # 简单的缓存机制
    
    def handle_validation_error(
        self, 
        message: MessageData, 
        error: ValidationResult
    ) -> None:
        """
        处理验证错误
        
        验证错误不应重试，直接拒绝消息并记录详细错误信息。
        
        实现要求：
        - Requirements 2.4: 处理发布失败
        - Requirements 3.5: 处理无效数据并记录错误
        - Requirements 8.3: 记录错误日志
        
        Args:
            message: 消息数据
            error: 验证结果
        """
        self._logger.error(
            f"Validation failed for message {message.message_id} "
            f"of type '{message.type}': {error.errors}",
            extra={
                "message_id": message.message_id,
                "message_type": message.type,
                "errors": error.errors,
                "warnings": error.warnings,
                "timestamp": message.timestamp.isoformat()
            }
        )
        
        # 验证错误不重试，直接拒绝
        # 调用者应该检查 PublishResult 的 success 字段
    
    def handle_database_error(
        self, 
        operation: Callable[[], Any],
        operation_name: str,
        error: Exception,
        max_retries: int = 3,
        initial_delay: float = 0.1
    ) -> Optional[Any]:
        """
        处理数据库错误
        
        使用指数退避策略重试数据库操作。如果所有重试都失败，
        尝试返回缓存数据或空结果。
        
        实现要求：
        - Requirements 8.3: 记录错误日志
        - 重试机制：最多重试 3 次，使用指数退避
        - 降级处理：返回缓存数据或空结果
        
        Args:
            operation: 要重试的操作（可调用对象）
            operation_name: 操作名称（用于日志）
            error: 原始异常
            max_retries: 最大重试次数（默认 3）
            initial_delay: 初始延迟时间（秒，默认 0.1）
            
        Returns:
            Optional[Any]: 操作结果，如果失败则返回缓存或 None
        """
        self._logger.error(
            f"Database error in operation '{operation_name}': {error}",
            extra={
                "operation": operation_name,
                "error_type": type(error).__name__,
                "error_message": str(error)
            },
            exc_info=True
        )
        
        # 尝试重试
        for attempt in range(max_retries):
            try:
                self._logger.info(
                    f"Retrying operation '{operation_name}' "
                    f"(attempt {attempt + 1}/{max_retries})"
                )
                result = operation()
                
                # 成功后缓存结果
                self._cache[operation_name] = result
                
                self._logger.info(
                    f"Operation '{operation_name}' succeeded on retry {attempt + 1}"
                )
                return result
                
            except Exception as retry_error:
                if attempt == max_retries - 1:
                    # 最后一次失败，尝试返回缓存或空结果
                    self._logger.error(
                        f"Operation '{operation_name}' failed after "
                        f"{max_retries} retries: {retry_error}",
                        extra={
                            "operation": operation_name,
                            "retries": max_retries,
                            "final_error": str(retry_error)
                        }
                    )
                    return self._get_cached_result(operation_name)
                
                # 指数退避
                delay = initial_delay * (2 ** attempt)
                self._logger.warning(
                    f"Retry {attempt + 1} failed for '{operation_name}', "
                    f"waiting {delay:.2f}s before next attempt"
                )
                time.sleep(delay)
        
        # 不应该到达这里，但为了安全返回缓存
        return self._get_cached_result(operation_name)
    
    def handle_subscriber_error(
        self, 
        subscriber_id: str, 
        error: Exception,
        message_id: Optional[str] = None
    ) -> None:
        """
        处理订阅者错误
        
        订阅者回调失败不应影响其他订阅者，只记录错误日志。
        
        实现要求：
        - Requirements 9.5: 订阅者错误隔离
        - Requirements 8.3: 记录错误日志
        
        Args:
            subscriber_id: 订阅者ID
            error: 异常对象
            message_id: 消息ID（可选）
        """
        log_extra = {
            "subscriber_id": subscriber_id,
            "error_type": type(error).__name__,
            "error_message": str(error)
        }
        
        if message_id:
            log_extra["message_id"] = message_id
            self._logger.error(
                f"Subscriber {subscriber_id} callback failed "
                f"for message {message_id}: {error}",
                extra=log_extra,
                exc_info=True
            )
        else:
            self._logger.error(
                f"Subscriber {subscriber_id} callback failed: {error}",
                extra=log_extra,
                exc_info=True
            )
        
        # 记录错误但不抛出异常，允许其他订阅者继续处理
    
    def _get_cached_result(self, operation_name: str) -> Optional[Any]:
        """
        获取缓存的结果
        
        Args:
            operation_name: 操作名称
            
        Returns:
            Optional[Any]: 缓存的结果，如果不存在则返回 None
        """
        if operation_name in self._cache:
            self._logger.info(
                f"Returning cached result for operation '{operation_name}'"
            )
            return self._cache[operation_name]
        
        self._logger.warning(
            f"No cached result available for operation '{operation_name}', "
            "returning None"
        )
        return None
    
    def clear_cache(self) -> None:
        """清除所有缓存"""
        self._cache.clear()
        self._logger.debug("Error handler cache cleared")
