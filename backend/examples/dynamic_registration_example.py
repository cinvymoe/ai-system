"""
Dynamic Message Type Registration Example

This example demonstrates how to dynamically register new message types
at runtime without modifying the core broker code.

Requirements demonstrated:
- 6.1: Generic interface for registering new message types
- 6.2: Create dedicated subscription channel
- 6.3: Support dynamic addition without code modification
- 6.4: Allow custom validation rules
- 6.5: Backward compatibility when extending
"""

from typing import Dict, Any
from datetime import datetime

from src.broker.broker import MessageBroker
from src.broker.handlers import MessageTypeHandler
from src.broker.models import ValidationResult, ProcessedMessage, MessageData


# Example 1: Simple custom message type
class TemperatureMessageHandler(MessageTypeHandler):
    """处理温度传感器消息"""
    
    MIN_TEMP = -50.0
    MAX_TEMP = 100.0
    
    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """验证温度数据"""
        errors = []
        warnings = []
        
        if 'temperature' not in data:
            errors.append("Missing required field: 'temperature'")
        else:
            try:
                temp = float(data['temperature'])
                if temp < self.MIN_TEMP or temp > self.MAX_TEMP:
                    errors.append(
                        f"Temperature {temp}°C is out of valid range "
                        f"[{self.MIN_TEMP}, {self.MAX_TEMP}]"
                    )
                elif temp > 40:
                    warnings.append(f"High temperature detected: {temp}°C")
            except (TypeError, ValueError):
                errors.append("Invalid temperature value")
        
        if 'sensor_id' not in data:
            warnings.append("Missing 'sensor_id' field")
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def process(self, data: Dict[str, Any]) -> ProcessedMessage:
        """处理温度消息"""
        processed_data = {
            'temperature': float(data['temperature']),
            'sensor_id': data.get('sensor_id', 'unknown'),
            'timestamp': data.get('timestamp', datetime.now().isoformat()),
            'unit': data.get('unit', 'celsius'),
        }
        
        message = MessageData(
            type=self.get_type_name(),
            data=processed_data,
            timestamp=datetime.now()
        )
        
        return ProcessedMessage(
            original=message,
            validated=True,
            cameras=[],
            processing_time=0.0,
            errors=[]
        )
    
    def get_type_name(self) -> str:
        return "temperature_sensor"


# Example 2: Complex custom message type with metadata
class SecurityEventHandler(MessageTypeHandler):
    """处理安全事件消息"""
    
    VALID_EVENT_TYPES = {
        'intrusion', 'fire', 'flood', 'power_failure', 'system_error'
    }
    
    VALID_PRIORITIES = {'low', 'medium', 'high', 'critical'}
    
    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """验证安全事件数据"""
        errors = []
        warnings = []
        
        # 验证事件类型
        if 'event_type' not in data:
            errors.append("Missing required field: 'event_type'")
        elif data['event_type'] not in self.VALID_EVENT_TYPES:
            errors.append(
                f"Invalid event_type '{data['event_type']}'. "
                f"Must be one of: {', '.join(self.VALID_EVENT_TYPES)}"
            )
        
        # 验证优先级
        if 'priority' not in data:
            warnings.append("Missing 'priority' field, will default to 'medium'")
        elif data['priority'] not in self.VALID_PRIORITIES:
            errors.append(
                f"Invalid priority '{data['priority']}'. "
                f"Must be one of: {', '.join(self.VALID_PRIORITIES)}"
            )
        
        # 验证位置信息
        if 'location' in data:
            location = data['location']
            if not isinstance(location, dict):
                errors.append("Field 'location' must be a dictionary")
            elif 'zone' not in location and 'coordinates' not in location:
                warnings.append(
                    "Location should include 'zone' or 'coordinates'"
                )
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def process(self, data: Dict[str, Any]) -> ProcessedMessage:
        """处理安全事件消息"""
        processed_data = {
            'event_type': data['event_type'],
            'priority': data.get('priority', 'medium'),
            'location': data.get('location', {}),
            'description': data.get('description', ''),
            'timestamp': data.get('timestamp', datetime.now().isoformat()),
            'metadata': data.get('metadata', {}),
        }
        
        message = MessageData(
            type=self.get_type_name(),
            data=processed_data,
            timestamp=datetime.now()
        )
        
        return ProcessedMessage(
            original=message,
            validated=True,
            cameras=[],
            processing_time=0.0,
            errors=[]
        )
    
    def get_type_name(self) -> str:
        return "security_event"


def main():
    """演示动态消息类型注册"""
    
    print("=== Dynamic Message Type Registration Example ===\n")
    
    # 获取消息代理实例
    broker = MessageBroker.get_instance()
    
    print("1. Initial registered types:")
    print(f"   {broker.get_registered_types()}\n")
    
    # 动态注册温度传感器消息类型
    print("2. Registering temperature sensor message type...")
    temp_handler = TemperatureMessageHandler()
    broker.register_message_type("temperature_sensor", temp_handler)
    print(f"   Registered types: {broker.get_registered_types()}\n")
    
    # 订阅温度消息
    print("3. Subscribing to temperature messages...")
    
    def on_temperature(msg: MessageData):
        temp = msg.data['temperature']
        sensor_id = msg.data['sensor_id']
        print(f"   📊 Temperature alert: {temp}°C from sensor {sensor_id}")
    
    broker.subscribe("temperature_sensor", on_temperature)
    
    # 发布温度消息
    print("\n4. Publishing temperature messages...")
    
    # 正常温度
    result1 = broker.publish("temperature_sensor", {
        "temperature": 22.5,
        "sensor_id": "TEMP-001",
        "unit": "celsius"
    })
    print(f"   Result: {result1.success}, notified {result1.subscribers_notified} subscribers")
    
    # 高温警告
    result2 = broker.publish("temperature_sensor", {
        "temperature": 45.0,
        "sensor_id": "TEMP-002"
    })
    print(f"   Result: {result2.success}, notified {result2.subscribers_notified} subscribers")
    
    # 无效温度（应该失败）
    result3 = broker.publish("temperature_sensor", {
        "temperature": 150.0,  # 超出范围
        "sensor_id": "TEMP-003"
    })
    print(f"   Result: {result3.success}, errors: {result3.errors}")
    
    # 动态注册安全事件消息类型
    print("\n5. Registering security event message type...")
    security_handler = SecurityEventHandler()
    broker.register_message_type("security_event", security_handler)
    print(f"   Registered types: {broker.get_registered_types()}\n")
    
    # 订阅安全事件
    print("6. Subscribing to security events...")
    
    def on_security_event(msg: MessageData):
        event_type = msg.data['event_type']
        priority = msg.data['priority']
        print(f"   🚨 Security event: {event_type} (priority: {priority})")
    
    broker.subscribe("security_event", on_security_event)
    
    # 发布安全事件
    print("\n7. Publishing security events...")
    
    result4 = broker.publish("security_event", {
        "event_type": "intrusion",
        "priority": "high",
        "location": {
            "zone": "Building A, Floor 2",
            "coordinates": {"x": 100, "y": 200}
        },
        "description": "Unauthorized access detected"
    })
    print(f"   Result: {result4.success}, notified {result4.subscribers_notified} subscribers")
    
    result5 = broker.publish("security_event", {
        "event_type": "fire",
        "priority": "critical",
        "location": {"zone": "Building B, Floor 1"}
    })
    print(f"   Result: {result5.success}, notified {result5.subscribers_notified} subscribers")
    
    # 演示类型隔离
    print("\n8. Demonstrating message type isolation...")
    print("   Temperature subscribers will NOT receive security events")
    print("   Security subscribers will NOT receive temperature messages")
    
    # 统计信息
    print("\n9. Broker statistics:")
    stats = broker.get_stats()
    print(f"   Messages published: {stats['messages_published']}")
    print(f"   Messages failed: {stats['messages_failed']}")
    print(f"   Total subscribers: {stats['subscribers_count']}")
    
    print("\n10. Subscriber counts by type:")
    for msg_type in broker.get_registered_types():
        count = broker.get_subscriber_count(msg_type)
        print(f"   {msg_type}: {count} subscribers")
    
    print("\n=== Example Complete ===")


if __name__ == "__main__":
    main()
