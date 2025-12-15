# Subscription Notification - Quick Start

## Basic Usage

### 1. Subscribe to Messages

```python
from broker.broker import MessageBroker
from broker.models import MessageData

# Get broker instance
broker = MessageBroker.get_instance()

# Define callback
def on_direction_change(message: MessageData):
    direction = message.data["command"]
    print(f"Direction: {direction}")

# Subscribe
sub_id = broker.subscribe("direction_result", on_direction_change)
```

### 2. Publish Messages

```python
from datetime import datetime

# Publish a message
result = broker.publish("direction_result", {
    "command": "forward",
    "intensity": 0.8,
    "timestamp": datetime.now().isoformat()
})

print(f"Notified {result.subscribers_notified} subscribers")
```

### 3. Unsubscribe

```python
# Unsubscribe when done
broker.unsubscribe("direction_result", sub_id)
```

## Available Message Types

- `direction_result`: Motion direction messages
- `angle_value`: Sensor angle messages
- `ai_alert`: AI alert messages (placeholder)

## Common Patterns

### Pattern 1: Component with Lifecycle

```python
class MyComponent:
    def __init__(self):
        self.broker = MessageBroker.get_instance()
        self.sub_id = None
    
    def start(self):
        self.sub_id = self.broker.subscribe(
            "direction_result", 
            self.on_message
        )
    
    def stop(self):
        if self.sub_id:
            self.broker.unsubscribe("direction_result", self.sub_id)
    
    def on_message(self, message: MessageData):
        # Process message
        pass
```

### Pattern 2: Multiple Message Types

```python
class MultiSubscriber:
    def __init__(self):
        self.broker = MessageBroker.get_instance()
        self.subscriptions = []
    
    def start(self):
        self.subscriptions.append(
            self.broker.subscribe("direction_result", self.on_direction)
        )
        self.subscriptions.append(
            self.broker.subscribe("angle_value", self.on_angle)
        )
    
    def stop(self):
        for sub_id in self.subscriptions:
            # Extract message type from sub_id or track separately
            self.broker.unsubscribe("direction_result", sub_id)
        self.subscriptions.clear()
    
    def on_direction(self, message: MessageData):
        pass
    
    def on_angle(self, message: MessageData):
        pass
```

### Pattern 3: Async Processing

```python
import queue
import threading

class AsyncProcessor:
    def __init__(self):
        self.broker = MessageBroker.get_instance()
        self.queue = queue.Queue()
        self.worker_thread = None
        self.running = False
    
    def start(self):
        self.running = True
        self.worker_thread = threading.Thread(target=self._worker)
        self.worker_thread.start()
        
        self.broker.subscribe("direction_result", self._on_message)
    
    def stop(self):
        self.running = False
        if self.worker_thread:
            self.worker_thread.join()
    
    def _on_message(self, message: MessageData):
        # Fast callback - just queue it
        self.queue.put(message)
    
    def _worker(self):
        while self.running:
            try:
                message = self.queue.get(timeout=1)
                # Do expensive processing here
                self._process(message)
            except queue.Empty:
                continue
    
    def _process(self, message: MessageData):
        # Expensive processing
        pass
```

## Error Handling

Always handle errors in callbacks:

```python
def safe_callback(message: MessageData):
    try:
        # Your processing logic
        process_message(message)
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        # Don't re-raise
```

## Monitoring

Check subscriber counts:

```python
# Total subscribers
total = broker.get_subscriber_count()

# Subscribers for specific type
direction_subs = broker.get_subscriber_count("direction_result")

# Get subscriber details
subscribers = broker.get_subscribers("direction_result")
for sub in subscribers:
    print(f"ID: {sub['subscription_id']}")
```

## Testing

Run tests:

```bash
cd backend
python test_broker_subscription.py
```

## More Information

See `SUBSCRIPTION_NOTIFICATION_GUIDE.md` for complete documentation.
