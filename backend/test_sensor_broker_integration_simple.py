#!/usr/bin/env python3
"""
Simple test for Sensor-Broker Integration

验证传感器数据与消息代理的集成功能（不依赖完整的传感器API）
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Add backend/src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_angle_message_integration():
    """测试角度消息集成功能"""
    print("=" * 60)
    print("测试角度消息集成功能")
    print("=" * 60)
    
    try:
        from broker.broker import MessageBroker
        from broker.handlers import AngleMessageHandler
        
        # Initialize broker and handler
        broker = MessageBroker.get_instance()
        angle_handler = AngleMessageHandler()
        broker.register_message_type("angle_value", angle_handler)
        
        print("✓ 消息代理和角度处理器初始化成功")
        
        # Track received messages
        received_messages = []
        
        def angle_callback(message_data):
            received_messages.append(message_data)
            print(f"  📡 接收到角度消息: {message_data.data['angle']}° (时间: {message_data.data['timestamp']})")
        
        # Subscribe to angle messages
        subscription_id = broker.subscribe("angle_value", angle_callback)
        print(f"✓ 订阅角度消息成功 (ID: {subscription_id})")
        
        # Simulate sensor data processing like in sensors.py
        mock_sensor_data = {
            '加速度X(g)': 0.01,
            '加速度Y(g)': -0.02,
            '加速度Z(g)': 0.98,
            '角速度X(°/s)': 0.5,
            '角速度Y(°/s)': -0.3,
            '角速度Z(°/s)': 0.1,
            '角度X(°)': 1.2,
            '角度Y(°)': -0.8,
            '角度Z(°)': 135.7,  # Test angle
            '温度(°C)': 25.3,
            '电量(%)': 85.0
        }
        
        print(f"\n📊 模拟传感器数据处理:")
        print(f"  原始角度Z: {mock_sensor_data['角度Z(°)']}°")
        
        # Extract angle Z like sensors.py does
        angle_z = mock_sensor_data.get('角度Z(°)', 0.0)
        timestamp = datetime.now().isoformat()
        
        # Publish angle message in the same format as sensors.py
        angle_message_data = {
            "angle": float(angle_z),
            "timestamp": timestamp
        }
        
        print(f"  发布消息格式: {angle_message_data}")
        
        # Publish the message
        result = broker.publish("angle_value", angle_message_data)
        
        if result.success:
            print(f"✓ 角度消息发布成功")
            print(f"  消息ID: {result.message_id}")
            print(f"  通知订阅者: {result.subscribers_notified}")
        else:
            print(f"✗ 角度消息发布失败: {result.errors}")
            return False
        
        # Verify message was received
        if len(received_messages) > 0:
            received_msg = received_messages[0]
            if received_msg.data["angle"] == angle_z:
                print("✓ 订阅者正确接收到角度消息")
            else:
                print(f"✗ 消息内容不匹配: 期望 {angle_z}, 实际 {received_msg.data['angle']}")
                return False
        else:
            print("✗ 订阅者未接收到消息")
            return False
        
        # Test multiple angle values
        test_angles = [0.0, 45.0, 90.0, 180.0, -90.0, 270.0]
        print(f"\n🔄 测试多个角度值: {test_angles}")
        
        for test_angle in test_angles:
            angle_data = {
                "angle": float(test_angle),
                "timestamp": datetime.now().isoformat()
            }
            
            result = broker.publish("angle_value", angle_data)
            if result.success:
                print(f"  ✓ {test_angle}° - 发布成功")
            else:
                print(f"  ✗ {test_angle}° - 发布失败: {result.errors}")
                return False
        
        # Test invalid angles
        invalid_angles = [400.0, -200.0, 500.0]
        print(f"\n❌ 测试无效角度值: {invalid_angles}")
        
        for invalid_angle in invalid_angles:
            angle_data = {
                "angle": float(invalid_angle),
                "timestamp": datetime.now().isoformat()
            }
            
            result = broker.publish("angle_value", angle_data)
            if not result.success:
                print(f"  ✓ {invalid_angle}° - 正确拒绝")
            else:
                print(f"  ✗ {invalid_angle}° - 应该被拒绝但被接受了")
                return False
        
        # Clean up
        broker.unsubscribe("angle_value", subscription_id)
        print("\n✓ 清理完成")
        
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_requirements_compliance():
    """测试需求合规性"""
    print("\n" + "=" * 60)
    print("测试需求合规性")
    print("=" * 60)
    
    try:
        from broker.broker import MessageBroker
        from broker.handlers import AngleMessageHandler
        
        broker = MessageBroker.get_instance()
        
        # Requirements 3.1: WHEN an angle value is published THEN the Message Broker SHALL accept the angle data with timestamp
        print("📋 测试需求 3.1: 接受带时间戳的角度数据")
        
        angle_data = {
            "angle": 45.0,
            "timestamp": datetime.now().isoformat()
        }
        
        result = broker.publish("angle_value", angle_data)
        if result.success:
            print("  ✓ 消息代理接受了带时间戳的角度数据")
        else:
            print(f"  ✗ 消息代理拒绝了有效的角度数据: {result.errors}")
            return False
        
        # Requirements 3.2: THE Message Broker SHALL validate that angle data is within valid range before accepting
        print("\n📋 测试需求 3.2: 验证角度数据在有效范围内")
        
        # Test valid range
        valid_angles = [-180.0, 0.0, 180.0, 360.0]
        for angle in valid_angles:
            data = {"angle": angle, "timestamp": datetime.now().isoformat()}
            result = broker.publish("angle_value", data)
            if not result.success:
                print(f"  ✗ 有效角度 {angle}° 被错误拒绝: {result.errors}")
                return False
        
        print("  ✓ 所有有效角度都被接受")
        
        # Test invalid range
        invalid_angles = [-181.0, 361.0, 500.0]
        for angle in invalid_angles:
            data = {"angle": angle, "timestamp": datetime.now().isoformat()}
            result = broker.publish("angle_value", data)
            if result.success:
                print(f"  ✗ 无效角度 {angle}° 被错误接受")
                return False
        
        print("  ✓ 所有无效角度都被正确拒绝")
        
        # Requirements 3.3: WHEN angle data is published THEN the Message Broker SHALL notify all registered angle subscribers
        print("\n📋 测试需求 3.3: 通知所有注册的角度订阅者")
        
        # Create multiple subscribers
        received_counts = [0, 0, 0]
        
        def create_callback(index):
            def callback(message_data):
                received_counts[index] += 1
            return callback
        
        # Subscribe multiple callbacks
        sub_ids = []
        for i in range(3):
            sub_id = broker.subscribe("angle_value", create_callback(i))
            sub_ids.append(sub_id)
        
        # Publish a message
        test_data = {"angle": 90.0, "timestamp": datetime.now().isoformat()}
        result = broker.publish("angle_value", test_data)
        
        if result.success and result.subscribers_notified == 3:
            print(f"  ✓ 通知了所有 {result.subscribers_notified} 个订阅者")
        else:
            print(f"  ✗ 期望通知 3 个订阅者，实际通知了 {result.subscribers_notified} 个")
            return False
        
        # Verify all callbacks were called
        if all(count == 1 for count in received_counts):
            print("  ✓ 所有订阅者回调都被正确调用")
        else:
            print(f"  ✗ 订阅者回调调用次数不正确: {received_counts}")
            return False
        
        # Clean up
        for sub_id in sub_ids:
            broker.unsubscribe("angle_value", sub_id)
        
        return True
        
    except Exception as e:
        print(f"✗ 需求合规性测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("传感器-消息代理集成测试 (简化版)")
    print("=" * 60)
    
    tests = [
        ("角度消息集成功能", test_angle_message_integration),
        ("需求合规性", test_requirements_compliance),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"\n✅ {test_name} - 通过")
            else:
                print(f"\n❌ {test_name} - 失败")
        except Exception as e:
            print(f"\n💥 {test_name} - 异常: {e}")
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed}/{total} 通过")
    print("=" * 60)
    
    if passed == total:
        print("🎉 所有测试通过！")
        print("📡 传感器-消息代理集成功能正常工作")
        print("✅ 满足需求 3.1 和 3.3：角度数据发布和订阅通知")
        return True
    else:
        print("❌ 部分测试失败，请检查集成实现")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)