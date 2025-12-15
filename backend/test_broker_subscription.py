"""
Test script for verifying the subscription notification mechanism.

This script tests:
1. Subscriber callback registration
2. Message distribution to all subscribers
3. Subscriber error isolation
4. Thread-safe protection
"""

import sys
import threading
import time
from datetime import datetime
from typing import List

# Add src to path
sys.path.insert(0, 'src')

from broker.broker import MessageBroker
from broker.handlers import DirectionMessageHandler, AngleMessageHandler
from broker.models import MessageData


def reset_broker():
    """Reset the broker singleton for testing"""
    # Clear the singleton instance
    MessageBroker._instance = None


def test_basic_subscription():
    """Test basic subscription and notification"""
    print("\n=== Test 1: Basic Subscription ===")
    
    reset_broker()
    broker = MessageBroker.get_instance()
    
    # Register message types
    broker.register_message_type("direction_result", DirectionMessageHandler())
    broker.register_message_type("angle_value", AngleMessageHandler())
    
    # Track received messages
    received_messages = []
    
    def callback(message: MessageData):
        received_messages.append(message)
        print(f"  Callback received: {message.type} - {message.data}")
    
    # Subscribe
    sub_id = broker.subscribe("direction_result", callback)
    print(f"  Subscribed with ID: {sub_id}")
    
    # Publish a message
    result = broker.publish("direction_result", {
        "command": "forward",
        "intensity": 0.8,
        "timestamp": datetime.now().isoformat()
    })
    
    print(f"  Publish result: success={result.success}, notified={result.subscribers_notified}")
    print(f"  Messages received: {len(received_messages)}")
    
    assert result.success, "Publish should succeed"
    assert result.subscribers_notified == 1, "Should notify 1 subscriber"
    assert len(received_messages) == 1, "Should receive 1 message"
    
    print("  ✓ Test passed!")


def test_multiple_subscribers():
    """Test multiple subscribers receive the same message"""
    print("\n=== Test 2: Multiple Subscribers ===")
    
    reset_broker()
    broker = MessageBroker.get_instance()
    broker.register_message_type("direction_result", DirectionMessageHandler())
    
    # Track received messages for each subscriber
    received_1 = []
    received_2 = []
    received_3 = []
    
    def callback_1(message: MessageData):
        received_1.append(message)
    
    def callback_2(message: MessageData):
        received_2.append(message)
    
    def callback_3(message: MessageData):
        received_3.append(message)
    
    # Subscribe multiple callbacks
    sub_id_1 = broker.subscribe("direction_result", callback_1)
    sub_id_2 = broker.subscribe("direction_result", callback_2)
    sub_id_3 = broker.subscribe("direction_result", callback_3)
    
    print(f"  Subscribed 3 callbacks")
    print(f"  Subscriber count: {broker.get_subscriber_count('direction_result')}")
    
    # Publish a message
    result = broker.publish("direction_result", {
        "command": "turn_left",
        "intensity": 0.5,
        "timestamp": datetime.now().isoformat()
    })
    
    print(f"  Publish result: notified={result.subscribers_notified}")
    print(f"  Received counts: {len(received_1)}, {len(received_2)}, {len(received_3)}")
    
    assert result.subscribers_notified == 3, "Should notify 3 subscribers"
    assert len(received_1) == 1, "Subscriber 1 should receive message"
    assert len(received_2) == 1, "Subscriber 2 should receive message"
    assert len(received_3) == 1, "Subscriber 3 should receive message"
    
    # Verify all received the same message
    assert received_1[0].message_id == received_2[0].message_id == received_3[0].message_id
    
    print("  ✓ Test passed!")


def test_subscriber_error_isolation():
    """Test that one subscriber's error doesn't affect others"""
    print("\n=== Test 3: Subscriber Error Isolation ===")
    
    reset_broker()
    broker = MessageBroker.get_instance()
    broker.register_message_type("angle_value", AngleMessageHandler())
    
    received_good_1 = []
    received_good_2 = []
    
    def good_callback_1(message: MessageData):
        received_good_1.append(message)
        print(f"  Good callback 1 received message")
    
    def bad_callback(message: MessageData):
        print(f"  Bad callback raising exception")
        raise Exception("Intentional error in callback")
    
    def good_callback_2(message: MessageData):
        received_good_2.append(message)
        print(f"  Good callback 2 received message")
    
    # Subscribe in order: good, bad, good
    broker.subscribe("angle_value", good_callback_1)
    broker.subscribe("angle_value", bad_callback)
    broker.subscribe("angle_value", good_callback_2)
    
    print(f"  Subscribed 3 callbacks (1 will fail)")
    
    # Publish a message
    result = broker.publish("angle_value", {
        "angle": 45.0,
        "timestamp": datetime.now().isoformat()
    })
    
    print(f"  Publish result: notified={result.subscribers_notified}")
    print(f"  Good callbacks received: {len(received_good_1)}, {len(received_good_2)}")
    
    # Should notify 2 out of 3 (the bad one fails but doesn't stop others)
    assert result.subscribers_notified == 2, "Should notify 2 subscribers (bad one fails)"
    assert len(received_good_1) == 1, "Good callback 1 should receive message"
    assert len(received_good_2) == 1, "Good callback 2 should receive message"
    
    print("  ✓ Test passed! Error isolation works correctly")


def test_message_type_isolation():
    """Test that subscribers only receive messages of their subscribed type"""
    print("\n=== Test 4: Message Type Isolation ===")
    
    reset_broker()
    broker = MessageBroker.get_instance()
    broker.register_message_type("direction_result", DirectionMessageHandler())
    broker.register_message_type("angle_value", AngleMessageHandler())
    
    direction_messages = []
    angle_messages = []
    
    def direction_callback(message: MessageData):
        direction_messages.append(message)
    
    def angle_callback(message: MessageData):
        angle_messages.append(message)
    
    # Subscribe to different types
    broker.subscribe("direction_result", direction_callback)
    broker.subscribe("angle_value", angle_callback)
    
    print(f"  Subscribed to direction_result and angle_value")
    
    # Publish direction message
    broker.publish("direction_result", {
        "command": "backward",
        "intensity": 0.6,
        "timestamp": datetime.now().isoformat()
    })
    
    # Publish angle message
    broker.publish("angle_value", {
        "angle": 90.0,
        "timestamp": datetime.now().isoformat()
    })
    
    print(f"  Direction messages received: {len(direction_messages)}")
    print(f"  Angle messages received: {len(angle_messages)}")
    
    assert len(direction_messages) == 1, "Should receive 1 direction message"
    assert len(angle_messages) == 1, "Should receive 1 angle message"
    assert direction_messages[0].type == "direction_result"
    assert angle_messages[0].type == "angle_value"
    
    print("  ✓ Test passed! Message type isolation works correctly")


def test_thread_safety():
    """Test thread-safe publishing and subscription"""
    print("\n=== Test 5: Thread Safety ===")
    
    reset_broker()
    broker = MessageBroker.get_instance()
    broker.register_message_type("direction_result", DirectionMessageHandler())
    
    received_messages = []
    lock = threading.Lock()
    
    def thread_safe_callback(message: MessageData):
        with lock:
            received_messages.append(message)
    
    # Subscribe
    broker.subscribe("direction_result", thread_safe_callback)
    
    print(f"  Starting 10 threads to publish messages concurrently")
    
    # Publish from multiple threads
    threads = []
    for i in range(10):
        def publish_message(index):
            broker.publish("direction_result", {
                "command": "forward",
                "intensity": 0.5 + (index * 0.01),
                "timestamp": datetime.now().isoformat()
            })
        
        thread = threading.Thread(target=publish_message, args=(i,))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads
    for thread in threads:
        thread.join()
    
    print(f"  All threads completed")
    print(f"  Messages received: {len(received_messages)}")
    
    assert len(received_messages) == 10, "Should receive all 10 messages"
    
    print("  ✓ Test passed! Thread safety works correctly")


def test_unsubscribe():
    """Test unsubscribe functionality"""
    print("\n=== Test 6: Unsubscribe ===")
    
    reset_broker()
    broker = MessageBroker.get_instance()
    broker.register_message_type("direction_result", DirectionMessageHandler())
    
    received_messages = []
    
    def callback(message: MessageData):
        received_messages.append(message)
    
    # Subscribe
    sub_id = broker.subscribe("direction_result", callback)
    print(f"  Subscribed with ID: {sub_id}")
    
    # Publish first message
    broker.publish("direction_result", {
        "command": "forward",
        "intensity": 0.7,
        "timestamp": datetime.now().isoformat()
    })
    
    print(f"  Messages received after first publish: {len(received_messages)}")
    assert len(received_messages) == 1
    
    # Unsubscribe
    success = broker.unsubscribe("direction_result", sub_id)
    print(f"  Unsubscribe result: {success}")
    assert success, "Unsubscribe should succeed"
    
    # Publish second message
    broker.publish("direction_result", {
        "command": "backward",
        "intensity": 0.8,
        "timestamp": datetime.now().isoformat()
    })
    
    print(f"  Messages received after second publish: {len(received_messages)}")
    assert len(received_messages) == 1, "Should not receive message after unsubscribe"
    
    print("  ✓ Test passed! Unsubscribe works correctly")


def main():
    """Run all tests"""
    print("=" * 60)
    print("Testing Subscription Notification Mechanism")
    print("=" * 60)
    
    try:
        test_basic_subscription()
        test_multiple_subscribers()
        test_subscriber_error_isolation()
        test_message_type_isolation()
        test_thread_safety()
        test_unsubscribe()
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
