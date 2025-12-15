"""
Message Type Handlers

定义不同消息类型的处理器，负责验证和处理消息数据。
"""

from abc import ABC, abstractmethod
from typing import Any, Dict
import logging

from .models import ValidationResult, ProcessedMessage, MessageData
from datetime import datetime

logger = logging.getLogger(__name__)


class MessageTypeHandler(ABC):
    """消息类型处理器抽象基类"""
    
    @abstractmethod
    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """
        验证消息数据
        
        Args:
            data: 消息数据
            
        Returns:
            ValidationResult: 验证结果
        """
        pass
    
    @abstractmethod
    def process(self, data: Dict[str, Any]) -> ProcessedMessage:
        """
        处理消息数据
        
        Args:
            data: 消息数据
            
        Returns:
            ProcessedMessage: 处理后的消息
        """
        pass
    
    @abstractmethod
    def get_type_name(self) -> str:
        """
        获取消息类型名称
        
        Returns:
            str: 消息类型名称
        """
        pass


class DirectionMessageHandler(MessageTypeHandler):
    """方向消息处理器"""
    
    VALID_COMMANDS = {
        'forward', 'backward', 'turn_left', 'turn_right', 'stationary'
    }
    
    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """
        验证方向消息数据
        
        必需字段：
        - command: 方向命令
        - timestamp: 时间戳
        """
        errors = []
        warnings = []
        
        # 检查必需字段
        if 'command' not in data:
            errors.append("Missing required field: 'command'")
        elif data['command'] not in self.VALID_COMMANDS:
            errors.append(
                f"Invalid command '{data['command']}'. "
                f"Must be one of: {', '.join(self.VALID_COMMANDS)}"
            )
        
        if 'timestamp' not in data:
            warnings.append("Missing 'timestamp' field, will use current time")
        
        # 可选字段验证
        if 'intensity' in data:
            try:
                intensity = float(data['intensity'])
                if intensity < 0:
                    warnings.append("Intensity should be non-negative")
            except (TypeError, ValueError):
                warnings.append("Invalid intensity value, should be a number")
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def process(self, data: Dict[str, Any]) -> ProcessedMessage:
        """处理方向消息"""
        # 标准化数据
        processed_data = {
            'command': data['command'],
            'timestamp': data.get('timestamp', datetime.now().isoformat()),
            'intensity': data.get('intensity', 0.0),
            'angular_intensity': data.get('angular_intensity', 0.0),
        }
        
        message = MessageData(
            type=self.get_type_name(),
            data=processed_data,
            timestamp=datetime.now()
        )
        
        return ProcessedMessage(
            original=message,
            validated=True,
            cameras=[],  # 将由 CameraMapper 填充
            processing_time=0.0,
            errors=[]
        )
    
    def get_type_name(self) -> str:
        return "direction_result"


class AngleMessageHandler(MessageTypeHandler):
    """角度消息处理器"""
    
    MIN_ANGLE = -180.0
    MAX_ANGLE = 360.0
    
    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """
        验证角度消息数据
        
        必需字段：
        - angle: 角度值
        - timestamp: 时间戳
        """
        errors = []
        warnings = []
        
        # 检查必需字段
        if 'angle' not in data:
            errors.append("Missing required field: 'angle'")
        else:
            try:
                angle = float(data['angle'])
                if angle < self.MIN_ANGLE or angle > self.MAX_ANGLE:
                    errors.append(
                        f"Angle {angle} is out of valid range "
                        f"[{self.MIN_ANGLE}, {self.MAX_ANGLE}]"
                    )
            except (TypeError, ValueError):
                errors.append("Invalid angle value, should be a number")
        
        if 'timestamp' not in data:
            warnings.append("Missing 'timestamp' field, will use current time")
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def process(self, data: Dict[str, Any]) -> ProcessedMessage:
        """处理角度消息"""
        # 标准化数据
        processed_data = {
            'angle': float(data['angle']),
            'timestamp': data.get('timestamp', datetime.now().isoformat()),
        }
        
        message = MessageData(
            type=self.get_type_name(),
            data=processed_data,
            timestamp=datetime.now()
        )
        
        return ProcessedMessage(
            original=message,
            validated=True,
            cameras=[],  # 将由 CameraMapper 填充
            processing_time=0.0,
            errors=[]
        )
    
    def get_type_name(self) -> str:
        return "angle_value"


class PassthroughHandler(MessageTypeHandler):
    """
    通用透传处理器
    
    不对数据进行任何处理，只做最基本的验证（检查data是否为字典）。
    适用于不需要特殊验证和处理逻辑的消息类型。
    
    使用示例：
        broker.register_message_type("custom_event", PassthroughHandler("custom_event"))
    """
    
    def __init__(self, message_type: str):
        """
        初始化透传处理器
        
        Args:
            message_type: 消息类型名称
        """
        self._message_type = message_type
    
    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """
        最基本的验证：只检查data是否为字典
        
        Args:
            data: 消息数据
            
        Returns:
            ValidationResult: 验证结果（总是通过，除非data不是字典）
        """
        errors = []
        warnings = []
        
        if not isinstance(data, dict):
            errors.append("Data must be a dictionary")
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def process(self, data: Dict[str, Any]) -> ProcessedMessage:
        """
        透传处理：不修改任何数据，直接返回
        
        Args:
            data: 消息数据
            
        Returns:
            ProcessedMessage: 包含原始数据的处理结果
        """
        message = MessageData(
            type=self.get_type_name(),
            data=data,  # 直接使用原始数据，不做任何修改
            timestamp=datetime.now()
        )
        
        logger.debug(f"Passthrough handler processed message type: {self._message_type}")
        
        return ProcessedMessage(
            original=message,
            validated=True,
            cameras=[],
            processing_time=0.0,
            errors=[]
        )
    
    def get_type_name(self) -> str:
        """返回消息类型名称"""
        return self._message_type


class AIAlertMessageHandler(MessageTypeHandler):
    """AI 报警消息处理器（预留接口）"""
    
    VALID_SEVERITIES = {'low', 'medium', 'high', 'critical'}
    
    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """
        验证 AI 报警消息数据
        
        必需字段：
        - alert_type: 报警类型
        - severity: 严重程度
        - timestamp: 时间戳
        """
        errors = []
        warnings = []
        
        # 检查必需字段
        if 'alert_type' not in data:
            errors.append("Missing required field: 'alert_type'")
        
        if 'severity' not in data:
            errors.append("Missing required field: 'severity'")
        elif data['severity'] not in self.VALID_SEVERITIES:
            errors.append(
                f"Invalid severity '{data['severity']}'. "
                f"Must be one of: {', '.join(self.VALID_SEVERITIES)}"
            )
        
        if 'timestamp' not in data:
            warnings.append("Missing 'timestamp' field, will use current time")
        
        # 预留：未来可以添加更多验证规则
        warnings.append(
            "AI alert handling is a placeholder implementation. "
            "Full functionality will be added when AI system is integrated."
        )
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def process(self, data: Dict[str, Any]) -> ProcessedMessage:
        """处理 AI 报警消息（预留实现）"""
        # 标准化数据
        processed_data = {
            'alert_type': data['alert_type'],
            'severity': data['severity'],
            'timestamp': data.get('timestamp', datetime.now().isoformat()),
            'metadata': data.get('metadata', {}),
        }
        
        message = MessageData(
            type=self.get_type_name(),
            data=processed_data,
            timestamp=datetime.now()
        )
        
        logger.info(
            f"AI alert processed (placeholder): {data['alert_type']} "
            f"with severity {data['severity']}"
        )
        
        return ProcessedMessage(
            original=message,
            validated=True,
            cameras=[],  # 将由 CameraMapper 填充（未来实现）
            processing_time=0.0,
            errors=[]
        )
    
    def get_type_name(self) -> str:
        return "ai_alert"
