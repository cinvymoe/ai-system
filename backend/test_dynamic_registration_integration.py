"""
Integration test for dynamic message type registration.

This test verifies that the dynamic registration feature works correctly
with the entire broker system including existing message types.
"""

import pytest
from typing import Dict, Any
from datetime import datetime

from src.broker.broker import MessageBroker
from src.broker.handlers import (
    MessageTypeHandler,
    DirectionMessageHandler,
    AngleMessageHandler,
    AIAlertMessageHandler
)
from src.broker.models import ValidationResult, ProcessedMessage, MessageData


class WeatherMessageHandler(MessageTypeHandler):
    """Weather sensor message handler for testing"""
    
    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        errors = []
        if 'temperature' not in data:
            errors.append("Missing temperature")
        if 'humidity' not in data:
            errors.append("Missing humidity")
        return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=[])
    
    def process(self, data: Dict[str, Any]) -> ProcessedMessage:
        message = MessageData(
            type=self.get_type_name(),
            data=data,
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
        return "weather_sensor"


def test_integration_with_existing_types():
    """Test that dynamic registration works alongside existing types"""
    # Reset broker
    MessageBroker._instance = None
    broker = MessageBroker.get_instance()
    
    # Register existing types
    broker.register_message_type("direction_result", DirectionMessageHandler())
    broker.register_message_type("angle_value", AngleMessageHandler())
    broker.register_message_type("ai_alert", AIAlertMessageHandler())
    
    # Track messages
    direction_messages = []
    angle_messages = []
    weather_messages = []
    
    def on_direction(msg):
        direction_messages.append(msg)
    
    def on_angle(msg):
        angle_messages.append(msg)
    
    def on_weather(msg):
        weather_messages.append(msg)
    
    # Subscribe to existing types
    broker.subscribe("direction_result", on_direction)
    broker.subscribe("angle_value", on_angle)
    
    # Publish to existing types
    broker.publish("direction_result", {
        "command": "forward",
        "timestamp": datetime.now().isoformat()
    })
    broker.publish("angle_value", {
        "angle": 45.0,
        "timestamp": datetime.now().isoformat()
    })
    
    assert len(direction_messages) == 1
    assert len(angle_messages) == 1
    assert len(weather_messages) == 0
    
    # Now dynamically add weather type
    broker.register_message_type("weather_sensor", WeatherMessageHandler())
    broker.subscribe("weather_sensor", on_weather)
    
    # Publish to all types
    broker.publish("direction_result", {
        "command": "backward",
        "timestamp": datetime.now().isoformat()
    })
    broker.publish("angle_value", {
        "angle": 90.0,
        "timestamp": datetime.now().isoformat()
    })
    broker.publish("weather_sensor", {
        "temperature": 22.5,
        "humidity": 65.0
    })
    
    # Verify all types work independently
    assert len(direction_messages) == 2
    assert len(angle_messages) == 2
    assert len(weather_messages) == 1
    
    # Verify message isolation
    assert direction_messages[0].type == "direction_result"
    assert angle_messages[0].type == "angle_value"
    assert weather_messages[0].type == "weather_sensor"
    
    # Cleanup
    broker.shutdown()
    MessageBroker._instance = None


def test_runtime_handler_replacement():
    """Test replacing a handler at runtime"""
    MessageBroker._instance = None
    broker = MessageBroker.get_instance()
    
    # Register initial handler
    handler1 = WeatherMessageHandler()
    broker.register_message_type("test_type", handler1)
    
    # Subscribe
    messages = []
    broker.subscribe("test_type", lambda msg: messages.append(msg))
    
    # Publish with first handler
    result1 = broker.publish("test_type", {
        "temperature": 20.0,
        "humidity": 50.0
    })
    assert result1.success
    assert len(messages) == 1
    
    # Replace handler
    class NewWeatherHandler(MessageTypeHandler):
        def validate(self, data):
            # More lenient validation
            return ValidationResult(valid=True, errors=[], warnings=[])
        
        def process(self, data):
            message = MessageData(
                type=self.get_type_name(),
                data=data,
                timestamp=datetime.now()
            )
            return ProcessedMessage(
                original=message,
                validated=True,
                cameras=[],
                processing_time=0.0,
                errors=[]
            )
        
        def get_type_name(self):
            return "test_type"
    
    handler2 = NewWeatherHandler()
    broker.register_message_type("test_type", handler2, allow_override=True)
    
    # Verify subscriber still works (backward compatibility)
    result2 = broker.publish("test_type", {
        "any_field": "any_value"  # Would fail with old handler
    })
    assert result2.success
    assert len(messages) == 2
    
    # Cleanup
    broker.shutdown()
    MessageBroker._instance = None


def test_multiple_dynamic_registrations():
    """Test registering multiple types dynamically"""
    MessageBroker._instance = None
    broker = MessageBroker.get_instance()
    
    # Create multiple handlers
    handlers = {}
    for i in range(5):
        class DynamicHandler(MessageTypeHandler):
            def __init__(self, type_id):
                self.type_id = type_id
            
            def validate(self, data):
                return ValidationResult(valid=True, errors=[], warnings=[])
            
            def process(self, data):
                message = MessageData(
                    type=self.get_type_name(),
                    data=data,
                    timestamp=datetime.now()
                )
                return ProcessedMessage(
                    original=message,
                    validated=True,
                    cameras=[],
                    processing_time=0.0,
                    errors=[]
                )
            
            def get_type_name(self):
                return f"dynamic_type_{self.type_id}"
        
        handler = DynamicHandler(i)
        handlers[f"dynamic_type_{i}"] = handler
        broker.register_message_type(f"dynamic_type_{i}", handler)
    
    # Verify all registered
    registered = broker.get_registered_types()
    for i in range(5):
        assert f"dynamic_type_{i}" in registered
    
    # Subscribe and publish to each
    message_counts = {f"dynamic_type_{i}": [] for i in range(5)}
    
    for type_name in message_counts.keys():
        broker.subscribe(
            type_name,
            lambda msg, tn=type_name: message_counts[tn].append(msg)
        )
    
    # Publish to each type
    for i in range(5):
        broker.publish(f"dynamic_type_{i}", {"data": f"test_{i}"})
    
    # Verify isolation
    for i in range(5):
        assert len(message_counts[f"dynamic_type_{i}"]) == 1
    
    # Cleanup
    broker.shutdown()
    MessageBroker._instance = None


def test_error_handling_with_dynamic_types():
    """Test error handling works correctly with dynamically registered types"""
    MessageBroker._instance = None
    broker = MessageBroker.get_instance()
    
    # Register type with strict validation
    broker.register_message_type("strict_type", WeatherMessageHandler())
    
    # Test validation error
    result = broker.publish("strict_type", {
        "temperature": 20.0
        # Missing humidity
    })
    
    assert not result.success
    assert len(result.errors) > 0
    assert "humidity" in result.errors[0].lower()
    
    # Test subscriber error isolation
    error_count = [0]
    success_count = [0]
    
    def failing_callback(msg):
        error_count[0] += 1
        raise Exception("Subscriber error")
    
    def working_callback(msg):
        success_count[0] += 1
    
    broker.subscribe("strict_type", failing_callback)
    broker.subscribe("strict_type", working_callback)
    
    # Publish valid message
    result = broker.publish("strict_type", {
        "temperature": 20.0,
        "humidity": 50.0
    })
    
    # Should succeed despite one subscriber failing
    assert result.success
    assert error_count[0] == 1
    assert success_count[0] == 1
    
    # Cleanup
    broker.shutdown()
    MessageBroker._instance = None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
