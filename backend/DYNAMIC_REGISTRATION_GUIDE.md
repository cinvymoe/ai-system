# Dynamic Message Type Registration Guide

## Overview

The Message Broker supports dynamic registration of new message types at runtime, enabling extensibility without modifying core broker code. This feature implements Requirements 6.1-6.5 from the design specification.

## Features

### 1. Generic Registration Interface (Requirement 6.1)

The broker provides a simple, generic interface for registering any message type:

```python
from src.broker.broker import MessageBroker
from src.broker.handlers import MessageTypeHandler

broker = MessageBroker.get_instance()
broker.register_message_type("my_custom_type", my_handler)
```

### 2. Dedicated Subscription Channels (Requirement 6.2)

Each registered message type automatically gets its own subscription channel:

```python
# Register type
broker.register_message_type("temperature", temp_handler)

# Subscribe to that specific type
def on_temperature(msg):
    print(f"Temperature: {msg.data['value']}")

broker.subscribe("temperature", on_temperature)
```

### 3. Dynamic Addition (Requirement 6.3)

New message types can be added at any time during runtime without modifying the broker:

```python
# Add types dynamically as needed
broker.register_message_type("type_1", handler_1)
broker.register_message_type("type_2", handler_2)
broker.register_message_type("type_3", handler_3)

# All types are immediately available
broker.publish("type_1", data_1)
broker.publish("type_2", data_2)
```

### 4. Custom Validation Rules (Requirement 6.4)

Each message type defines its own validation logic through its handler:

```python
class MyHandler(MessageTypeHandler):
    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        errors = []
        
        # Custom validation logic
        if 'required_field' not in data:
            errors.append("Missing required field")
        
        if data.get('value', 0) < 0:
            errors.append("Value must be non-negative")
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=[]
        )
```

### 5. Backward Compatibility (Requirement 6.5)

Existing message types and subscribers continue to work when new types are added:

```python
# Existing type with subscribers
broker.register_message_type("old_type", old_handler)
broker.subscribe("old_type", old_callback)

# Add new type - doesn't affect existing type
broker.register_message_type("new_type", new_handler)

# Old subscribers still work
broker.publish("old_type", data)  # old_callback is called
```

## Creating a Custom Message Handler

To create a custom message type, implement the `MessageTypeHandler` interface:

```python
from typing import Dict, Any
from datetime import datetime
from src.broker.handlers import MessageTypeHandler
from src.broker.models import ValidationResult, ProcessedMessage, MessageData

class MyCustomHandler(MessageTypeHandler):
    """Custom message handler"""
    
    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """
        Validate message data.
        
        Returns:
            ValidationResult with valid flag, errors, and warnings
        """
        errors = []
        warnings = []
        
        # Add your validation logic here
        if 'required_field' not in data:
            errors.append("Missing required field: 'required_field'")
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def process(self, data: Dict[str, Any]) -> ProcessedMessage:
        """
        Process and normalize message data.
        
        Returns:
            ProcessedMessage with normalized data
        """
        # Normalize/transform data as needed
        processed_data = {
            'field1': data.get('field1', 'default'),
            'field2': data.get('field2', 0),
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
            cameras=[],
            processing_time=0.0,
            errors=[]
        )
    
    def get_type_name(self) -> str:
        """Return the message type name"""
        return "my_custom_type"
```

## Registration API

### Basic Registration

```python
broker.register_message_type(message_type, handler)
```

- `message_type`: String identifier for the message type
- `handler`: Instance of a class implementing `MessageTypeHandler`

### Registration with Override

```python
broker.register_message_type(message_type, handler, allow_override=True)
```

Use `allow_override=True` to replace an existing handler. This is useful for:
- Hot-reloading handlers during development
- Updating validation rules at runtime
- A/B testing different implementations

**Note**: When overriding, existing subscribers are preserved (backward compatibility).

### Check if Type is Registered

```python
if broker.is_type_registered("my_type"):
    print("Type is registered")
```

### Get Registered Types

```python
types = broker.get_registered_types()
print(f"Available types: {types}")
```

### Unregister a Type

```python
success = broker.unregister_message_type("my_type")
```

**Note**: Unregistering preserves the subscriber list for backward compatibility. If the type is re-registered, existing subscribers will still work.

## Handler Interface Validation

The broker validates that handlers implement the required interface:

```python
# This will raise MessageTypeError
class InvalidHandler:
    pass  # Missing required methods

broker.register_message_type("invalid", InvalidHandler())
# Raises: MessageTypeError: Handler must implement validate() method
```

Required methods:
- `validate(data: Dict[str, Any]) -> ValidationResult`
- `process(data: Dict[str, Any]) -> ProcessedMessage`
- `get_type_name() -> str`

## Thread Safety

All registration operations are thread-safe:

```python
import threading

def register_type(type_name, handler):
    broker.register_message_type(type_name, handler)

# Safe to register from multiple threads
threads = [
    threading.Thread(target=register_type, args=(f"type_{i}", handler))
    for i in range(10)
]

for t in threads:
    t.start()
for t in threads:
    t.join()
```

## Best Practices

### 1. Validate Handler Interface

Always ensure your handler implements all required methods:

```python
# Good: Implements all required methods
class GoodHandler(MessageTypeHandler):
    def validate(self, data): ...
    def process(self, data): ...
    def get_type_name(self): ...
```

### 2. Use Descriptive Type Names

```python
# Good: Clear and descriptive
broker.register_message_type("temperature_sensor", handler)
broker.register_message_type("security_alert", handler)

# Bad: Vague or unclear
broker.register_message_type("type1", handler)
broker.register_message_type("data", handler)
```

### 3. Provide Comprehensive Validation

```python
def validate(self, data: Dict[str, Any]) -> ValidationResult:
    errors = []
    warnings = []
    
    # Check required fields
    for field in ['field1', 'field2']:
        if field not in data:
            errors.append(f"Missing required field: '{field}'")
    
    # Validate data types
    if 'value' in data and not isinstance(data['value'], (int, float)):
        errors.append("Field 'value' must be a number")
    
    # Validate ranges
    if 'temperature' in data:
        temp = data['temperature']
        if temp < -50 or temp > 100:
            errors.append(f"Temperature {temp} out of range [-50, 100]")
    
    # Add warnings for optional issues
    if 'timestamp' not in data:
        warnings.append("Missing 'timestamp', will use current time")
    
    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings
    )
```

### 4. Handle Missing Optional Fields

```python
def process(self, data: Dict[str, Any]) -> ProcessedMessage:
    # Use .get() with defaults for optional fields
    processed_data = {
        'required_field': data['required_field'],  # Required
        'optional_field': data.get('optional_field', 'default'),  # Optional
        'timestamp': data.get('timestamp', datetime.now().isoformat()),
    }
    # ...
```

### 5. Document Your Handler

```python
class MyHandler(MessageTypeHandler):
    """
    Handler for XYZ messages.
    
    Required fields:
    - field1: Description of field1
    - field2: Description of field2
    
    Optional fields:
    - field3: Description of field3 (default: value)
    
    Validation rules:
    - field1 must be non-empty string
    - field2 must be in range [0, 100]
    """
```

## Examples

See `backend/examples/dynamic_registration_example.py` for complete working examples including:
- Temperature sensor message type
- Security event message type
- Subscription and publishing
- Validation demonstrations

## Testing

Run the test suite to verify dynamic registration:

```bash
cd backend
python -m pytest test_dynamic_registration.py -v
```

Tests cover:
- Basic registration
- Dedicated subscription channels
- Dynamic addition
- Custom validation rules
- Backward compatibility
- Override functionality
- Unregistration
- Interface validation
- Type isolation

## Troubleshooting

### Error: "Message type already registered"

**Cause**: Attempting to register a type that already exists without `allow_override=True`.

**Solution**: Either use a different type name or set `allow_override=True`:

```python
broker.register_message_type("my_type", handler, allow_override=True)
```

### Error: "Handler must implement X method"

**Cause**: Handler doesn't implement required interface methods.

**Solution**: Ensure your handler class implements all required methods:
- `validate()`
- `process()`
- `get_type_name()`

### Error: "Message type not registered"

**Cause**: Attempting to publish or subscribe to an unregistered type.

**Solution**: Register the type before using it:

```python
broker.register_message_type("my_type", handler)
broker.subscribe("my_type", callback)  # Now works
```

## Related Documentation

- [Broker Implementation Summary](BROKER_IMPLEMENTATION_SUMMARY.md)
- [Subscription Guide](SUBSCRIPTION_NOTIFICATION_GUIDE.md)
- [Error Handler Guide](ERROR_HANDLER_GUIDE.md)
- [Design Document](../.kiro/specs/sensor-camera-message-broker/design.md)
