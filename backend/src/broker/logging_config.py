"""
Logging Configuration for Message Broker

提供结构化日志配置，支持可配置的日志级别和格式。

实现要求：
- Requirements 8.1: 记录消息发布日志
- Requirements 8.2: 记录订阅注册日志
- Requirements 8.3: 记录错误日志
- Requirements 8.4: 支持可配置日志级别
"""

import logging
import logging.config
import sys
from typing import Any, Dict, Optional
from datetime import datetime
import json


class StructuredFormatter(logging.Formatter):
    """
    结构化日志格式化器
    
    将日志输出为 JSON 格式，便于日志分析和监控。
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        格式化日志记录为 JSON
        
        Args:
            record: 日志记录对象
            
        Returns:
            str: JSON 格式的日志字符串
        """
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # 添加额外的上下文信息
        if hasattr(record, "message_id"):
            log_data["message_id"] = record.message_id
        if hasattr(record, "message_type"):
            log_data["message_type"] = record.message_type
        if hasattr(record, "subscriber_id"):
            log_data["subscriber_id"] = record.subscriber_id
        if hasattr(record, "operation"):
            log_data["operation"] = record.operation
        
        # 添加异常信息
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # 添加所有 extra 字段
        for key, value in record.__dict__.items():
            if key not in [
                "name", "msg", "args", "created", "filename", "funcName",
                "levelname", "levelno", "lineno", "module", "msecs",
                "message", "pathname", "process", "processName",
                "relativeCreated", "thread", "threadName", "exc_info",
                "exc_text", "stack_info", "getMessage", "message_id",
                "message_type", "subscriber_id", "operation"
            ]:
                log_data[key] = value
        
        return json.dumps(log_data, ensure_ascii=False)


class SimpleFormatter(logging.Formatter):
    """
    简单的人类可读日志格式化器
    
    用于开发环境，提供易读的日志输出。
    """
    
    def __init__(self):
        super().__init__(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )


def configure_broker_logging(
    log_level: str = "INFO",
    use_structured: bool = False,
    log_file: Optional[str] = None
) -> None:
    """
    配置消息代理的日志系统
    
    实现要求：
    - Requirements 8.4: 支持可配置日志级别
    - 支持结构化日志（JSON 格式）
    - 支持文件和控制台输出
    
    Args:
        log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        use_structured: 是否使用结构化日志（JSON 格式）
        log_file: 日志文件路径（可选）
    """
    # 验证日志级别
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    log_level = log_level.upper()
    if log_level not in valid_levels:
        log_level = "INFO"
    
    # 选择格式化器
    if use_structured:
        formatter_class = StructuredFormatter
        formatter_config = {}
    else:
        formatter_class = SimpleFormatter
        formatter_config = {}
    
    # 配置处理器
    handlers = {
        "console": {
            "class": "logging.StreamHandler",
            "level": log_level,
            "formatter": "default",
            "stream": "ext://sys.stdout",
        }
    }
    
    # 如果指定了日志文件，添加文件处理器
    if log_file:
        handlers["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": log_level,
            "formatter": "default",
            "filename": log_file,
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "encoding": "utf-8",
        }
    
    # 日志配置字典
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": formatter_class,
                **formatter_config
            }
        },
        "handlers": handlers,
        "loggers": {
            "src.broker": {
                "level": log_level,
                "handlers": list(handlers.keys()),
                "propagate": False,
            },
            # 也配置根 broker 模块（如果从不同路径导入）
            "broker": {
                "level": log_level,
                "handlers": list(handlers.keys()),
                "propagate": False,
            },
        },
        "root": {
            "level": log_level,
            "handlers": list(handlers.keys()),
        }
    }
    
    # 应用配置
    logging.config.dictConfig(config)
    
    # 记录配置信息
    logger = logging.getLogger("src.broker")
    logger.info(
        f"Broker logging configured: level={log_level}, "
        f"structured={use_structured}, file={log_file}"
    )


def get_broker_logger(name: str) -> logging.Logger:
    """
    获取消息代理的日志记录器
    
    Args:
        name: 日志记录器名称（通常是模块名）
        
    Returns:
        logging.Logger: 日志记录器实例
    """
    # 确保名称以 broker 开头
    if not name.startswith("src.broker") and not name.startswith("broker"):
        name = f"src.broker.{name}"
    
    return logging.getLogger(name)


class BrokerLoggerAdapter(logging.LoggerAdapter):
    """
    消息代理日志适配器
    
    自动添加上下文信息到日志记录中。
    """
    
    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        """
        处理日志消息，添加上下文信息
        
        Args:
            msg: 日志消息
            kwargs: 关键字参数
            
        Returns:
            tuple: (消息, 关键字参数)
        """
        # 合并上下文信息
        extra = kwargs.get("extra", {})
        extra.update(self.extra)
        kwargs["extra"] = extra
        
        return msg, kwargs


def create_message_logger(
    message_id: str,
    message_type: str,
    base_logger: Optional[logging.Logger] = None
) -> BrokerLoggerAdapter:
    """
    创建带消息上下文的日志记录器
    
    Args:
        message_id: 消息ID
        message_type: 消息类型
        base_logger: 基础日志记录器（可选）
        
    Returns:
        BrokerLoggerAdapter: 带上下文的日志适配器
    """
    if base_logger is None:
        base_logger = get_broker_logger("broker")
    
    return BrokerLoggerAdapter(
        base_logger,
        {
            "message_id": message_id,
            "message_type": message_type,
        }
    )


def create_subscriber_logger(
    subscriber_id: str,
    base_logger: Optional[logging.Logger] = None
) -> BrokerLoggerAdapter:
    """
    创建带订阅者上下文的日志记录器
    
    Args:
        subscriber_id: 订阅者ID
        base_logger: 基础日志记录器（可选）
        
    Returns:
        BrokerLoggerAdapter: 带上下文的日志适配器
    """
    if base_logger is None:
        base_logger = get_broker_logger("broker")
    
    return BrokerLoggerAdapter(
        base_logger,
        {
            "subscriber_id": subscriber_id,
        }
    )


# 默认配置
def setup_default_logging(log_level: str = "INFO") -> None:
    """
    设置默认的日志配置
    
    Args:
        log_level: 日志级别
    """
    configure_broker_logging(
        log_level=log_level,
        use_structured=False,
        log_file=None
    )
