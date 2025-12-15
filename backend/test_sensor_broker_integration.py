#!/usr/bin/env python3
"""
Test script for Sensor-Broker Integration

验证传感器 WebSocket 与消息代理的集成功能
"""

import sys
import asyncio
import json
import logging
from pathlib import Path
from datetime import datetime

# Add backend/src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """测试导入"""
    print("=" * 60)
    print("测试导入")
    print("=" * 60)
    
    try:
        # Test broker imports
        from broker.broker import MessageBroker
        from broker.handlers import AngleMessageHandler
        print("✓ MessageBroker 和 AngleMessageHandler 导入成功")
        
        # Test sensor API imports
        from api.sensors import router
        print("✓ Sensor API 导入成功")
        
        return True
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_message_broker_setup():
    """测试消息代理设置"""
    print("\n" + "=" * 60)
    print("测试消息代理设置")
    print("=" * 60)
    
    try:
        from broker.broker import MessageBroker
        from broker.handlers import AngleMessageHandler
        
        # Get broker instance
        broker = MessageBroker.get_instance()
        print("✓ 获取 MessageBroker 单例实例成功")
        
        # Register angle message handler
        angle_handler = AngleMessageHandler()
        broker.register_message_type("angle_value", angle_handler)
        print("✓ 注册 AngleMessageHandler 成功")
        
        # Verify registration
        registered_types = broker.get_registered_types()
        if "angle_value" in registered_types:
            print("✓ angle_value 消息类型已注册")
        else:
            print("✗ angle_value 消息类型未找到")
            return False
        
        return True
    except Exception as e:
        print(f"✗ 消息代理设置失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_angle_message_publishing():
    """测试角度消息发布"""
    print("\n" + "=" * 60)
    print("测试角度消息发布")
    print("=" * 60)
    
    try:
        from broker.broker import MessageBroker
        
        broker = MessageBroker.get_instance()
        
        # Test data similar to what sensor API would send
        test_angle_data = {
            "angle": 45.5,
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"发布测试角度消息: {test_angle_data}")
        
        # Publish angle message
        result = broker.publish("angle_value", test_angle_data)
        
        if result.success:
            print(f"✓ 角度消息发布成功 (message_id: {result.message_id})")
            print(f"  通知了 {result.subscribers_notified} 个订阅者")
        else:
            print(f"✗ 角度消息发布失败: {result.errors}")
            return False
        
        # Test invalid angle data
        invalid_data = {
            "angle": 400.0,  # Out of valid range
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"发布无效角度消息: {invalid_data}")
        result = broker.publish("angle_value", invalid_data)
        
        if not result.success:
            print("✓ 无效角度消息被正确拒绝")
        else:
            print("✗ 无效角度消息应该被拒绝")
            return False
        
        return True
    except Exception as e:
        print(f"✗ 角度消息发布测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_subscription():
    """测试订阅功能"""
    print("\n" + "=" * 60)
    print("测试订阅功能")
    print("=" * 60)
    
    try:
        from broker.broker import MessageBroker
        
        broker = MessageBroker.get_instance()
        
        # Track received messages
        received_messages = []
        
        def angle_callback(message_data):
            received_messages.append(message_data)
            print(f"  收到角度消息: {message_data.data}")
        
        # Subscribe to angle messages
        subscription_id = broker.subscribe("angle_value", angle_callback)
        print(f"✓ 订阅角度消息成功 (subscription_id: {subscription_id})")
        
        # Publish a test message
        test_data = {
            "angle": 90.0,
            "timestamp": datetime.now().isoformat()
        }
        
        result = broker.publish("angle_value", test_data)
        
        if result.success and len(received_messages) > 0:
            print("✓ 订阅者成功接收到消息")
            received_msg = received_messages[0]
            if received_msg.data["angle"] == 90.0:
                print("✓ 消息内容正确")
            else:
                print(f"✗ 消息内容不匹配: 期望 90.0, 实际 {received_msg.data['angle']}")
                return False
        else:
            print("✗ 订阅者未接收到消息")
            return False
        
        # Unsubscribe
        unsubscribe_success = broker.unsubscribe("angle_value", subscription_id)
        if unsubscribe_success:
            print("✓ 取消订阅成功")
        else:
            print("✗ 取消订阅失败")
            return False
        
        return True
    except Exception as e:
        print(f"✗ 订阅测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_sensor_data_format():
    """测试传感器数据格式兼容性"""
    print("\n" + "=" * 60)
    print("测试传感器数据格式兼容性")
    print("=" * 60)
    
    try:
        from broker.broker import MessageBroker
        from broker.handlers import AngleMessageHandler
        
        # Simulate sensor data format from mock sensor
        mock_sensor_data = {
            '加速度X(g)': 0.01,
            '加速度Y(g)': -0.02,
            '加速度Z(g)': 0.98,
            '角速度X(°/s)': 0.5,
            '角速度Y(°/s)': -0.3,
            '角速度Z(°/s)': 0.1,
            '角度X(°)': 1.2,
            '角度Y(°)': -0.8,
            '角度Z(°)': 45.5,  # This is what we'll publish
            '温度(°C)': 25.3,
            '电量(%)': 85.0
        }
        
        # Extract angle Z as the sensor API would do
        angle_z = mock_sensor_data.get('角度Z(°)', 0.0)
        
        # Create message in the format that sensor API would send
        angle_message = {
            "angle": float(angle_z),
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"模拟传感器数据: 角度Z = {angle_z}°")
        print(f"转换后的消息格式: {angle_message}")
        
        # Validate with AngleMessageHandler
        handler = AngleMessageHandler()
        validation_result = handler.validate(angle_message)
        
        if validation_result.valid:
            print("✓ 消息格式验证通过")
        else:
            print(f"✗ 消息格式验证失败: {validation_result.errors}")
            return False
        
        # Test publishing
        broker = MessageBroker.get_instance()
        result = broker.publish("angle_value", angle_message)
        
        if result.success:
            print("✓ 传感器格式的角度消息发布成功")
        else:
            print(f"✗ 传感器格式的角度消息发布失败: {result.errors}")
            return False
        
        return True
    except Exception as e:
        print(f"✗ 传感器数据格式测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("传感器-消息代理集成测试")
    print("=" * 60)
    
    tests = [
        ("导入测试", test_imports),
        ("消息代理设置", test_message_broker_setup),
        ("角度消息发布", test_angle_message_publishing),
        ("订阅功能", test_subscription),
        ("传感器数据格式", test_sensor_data_format),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"\n✓ {test_name} - 通过")
            else:
                print(f"\n✗ {test_name} - 失败")
        except Exception as e:
            print(f"\n✗ {test_name} - 异常: {e}")
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed}/{total} 通过")
    print("=" * 60)
    
    if passed == total:
        print("🎉 所有测试通过！传感器-消息代理集成正常工作")
        return True
    else:
        print("❌ 部分测试失败，请检查集成实现")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)