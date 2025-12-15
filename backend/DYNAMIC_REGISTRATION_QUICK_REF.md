# Dynamic Message Type Registration - Quick Reference

## Quick Start

### 1. Create a Handler

```python
from src.broker.handlers import MessageTypeHandler
from src.broker.models import ValidationResult, ProcessedMessage, MessageData

class MyHandler(MessageTypeHandler):
    def validate(self, data):
        errors = []
        if 'required_field' not in data:
            errors.append("Missing required_field")
        return ValidationResult(valid=len(errors)==0, errors=errors, warnings=[])
    
    def process(self, data):
        message = MessageData(type=self.get_type_name(), data=data, timestamp=datetime.now())
        return ProcessedMessage(original=message, validated=True, cameras=[], processing_time=0.0, errors=[])
    
    def get_type_name(self):
        return "my_type"
```

### 2. Register the Type

```python
from src.broker.broker import MessageBroker

broker = MessageBroker.get_instance()
broker.register_message_type("my_type", MyHandler())
```

### 3. Subscribe and Publish

```python
# Subscribe
def callback(msg):
    print(f"Received: {msg.data}")

broker.subscribe("my_type", callback)

# Publish
result = broker.publish("my_type", {"required_field": "value"})
```

## Common Operations

### Check if Type Exists
```python
if broker.is_type_registered("my_type"):
    print("Type exists")
```

### Override Handler
```python
broker.register_message_type("my_type", NewHandler(), allow_override=True)
```

### Unregister Type
```python
broker.unregister_message_type("my_type")
```

### Get All Types
```python
types = broker.get_registered_types()
```

### Get Handler
```python
handler = broker.get_handler("my_type")
```

## Requirements Mapping

| Requirement | Feature | Method |
|-------------|---------|--------|
| 6.1 | Generic interface | `register_message_type()` |
| 6.2 | Dedicated channel | Automatic on registration |
| 6.3 | Dynamic addition | Runtime registration |
| 6.4 | Custom validation | Handler `validate()` method |
| 6.5 | Backward compatibility | Preserved subscribers on override |

## Testing

```bash
# Run all dynamic registration tests
cd backend
python -m pytest test_dynamic_registration*.py -v

# Run integration tests
python -m pytest test_dynamic_registration_integration.py -v

# Run example
python examples/dynamic_registration_example.py
```

## Files

- **Implementation**: `backend/src/broker/broker.py`
- **Tests**: `backend/test_dynamic_registration.py`
- **Integration Tests**: `backend/test_dynamic_registration_integration.py`
- **Example**: `backend/examples/dynamic_registration_example.py`
- **Guide**: `backend/DYNAMIC_REGISTRATION_GUIDE.md`
- **Summary**: `backend/DYNAMIC_REGISTRATION_SUMMARY.md`

## Key Points

✅ Thread-safe registration  
✅ Interface validation  
✅ Override support  
✅ Backward compatible  
✅ Type isolation  
✅ Custom validation per type  
✅ Runtime extensibility  

## Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| "already registered" | Type exists | Use `allow_override=True` |
| "must implement X" | Invalid handler | Implement required methods |
| "not registered" | Type doesn't exist | Register type first |

## See Also

- [Full Guide](DYNAMIC_REGISTRATION_GUIDE.md)
- [Implementation Summary](DYNAMIC_REGISTRATION_SUMMARY.md)
- [Broker Documentation](BROKER_IMPLEMENTATION_SUMMARY.md)
