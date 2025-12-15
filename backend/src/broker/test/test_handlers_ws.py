"""
WebSocket 测试脚本 - 测试 DirectionMessageHandler 和 AngleMessageHandler

通过 WebSocket 发送消息到 ws://localhost:8000/api/sensor/stream
测试 broker 的消息处理功能
"""

import asyncio
import websockets
import json
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BrokerHandlerTester:
    """Broker Handler WebSocket 测试器"""
    
    def __init__(self, ws_url: str = "ws://localhost:8000/api/sensor/stream"):
        self.ws_url = ws_url
        self.websocket = None
    
    async def connect(self):
        """连接到 WebSocket 服务器"""
        try:
            self.websocket = await websockets.connect(self.ws_url)
            logger.info(f"✓ 已连接到 {self.ws_url}")
            return True
        except Exception as e:
            logger.error(f"✗ 连接失败: {e}")
            return False
    
    async def send_message(self, message: dict):
        """发送消息"""
        if not self.websocket:
            logger.error("WebSocket 未连接")
            return False
        
        try:
            message_json = json.dumps(message)
            await self.websocket.send(message_json)
            logger.info(f"→ 发送消息: {message_json}")
            return True
        except Exception as e:
            logger.error(f"✗ 发送失败: {e}")
            return False
    
    async def receive_message(self, timeout: float = 2.0):
        """接收消息"""
        if not self.websocket:
            logger.error("WebSocket 未连接")
            return None
        
        try:
            response = await asyncio.wait_for(
                self.websocket.recv(),
                timeout=timeout
            )
            logger.info(f"← 收到响应: {response}")
            return json.loads(response)
        except asyncio.TimeoutError:
            logger.warning("⚠ 接收超时")
            return None
        except Exception as e:
            logger.error(f"✗ 接收失败: {e}")
            return None
    
    async def close(self):
        """关闭连接"""
        if self.websocket:
            await self.websocket.close()
            logger.info("✓ 连接已关闭")
    
    # ========== DirectionMessageHandler 测试 ==========
    
    async def test_direction_forward(self):
        """测试前进方向消息"""
        logger.info("\n=== 测试 1: 前进方向 ===")
        message = {
            "type": "direction_result",
            "data": {
                "command": "forward",
                "timestamp": datetime.now().isoformat(),
                "intensity": 0.8,
                "angular_intensity": 0.0
            }
        }
        await self.send_message(message)
        response = await self.receive_message()
        return response
    
    async def test_direction_turn_left(self):
        """测试左转方向消息"""
        logger.info("\n=== 测试 2: 左转方向 ===")
        message = {
            "type": "direction_result",
            "data": {
                "command": "turn_left",
                "timestamp": datetime.now().isoformat(),
                "intensity": 0.5,
                "angular_intensity": 0.6
            }
        }
        await self.send_message(message)
        response = await self.receive_message()
        return response
    
    async def test_direction_turn_right(self):
        """测试右转方向消息"""
        logger.info("\n=== 测试 3: 右转方向 ===")
        message = {
            "type": "direction_result",
            "data": {
                "command": "turn_right",
                "timestamp": datetime.now().isoformat(),
                "intensity": 0.5,
                "angular_intensity": 0.7
            }
        }
        await self.send_message(message)
        response = await self.receive_message()
        return response
    
    async def test_direction_backward(self):
        """测试后退方向消息"""
        logger.info("\n=== 测试 4: 后退方向 ===")
        message = {
            "type": "direction_result",
            "data": {
                "command": "backward",
                "timestamp": datetime.now().isoformat(),
                "intensity": 0.6,
                "angular_intensity": 0.0
            }
        }
        await self.send_message(message)
        response = await self.receive_message()
        return response
    
    async def test_direction_stationary(self):
        """测试静止方向消息"""
        logger.info("\n=== 测试 5: 静止状态 ===")
        message = {
            "type": "direction_result",
            "data": {
                "command": "stationary",
                "timestamp": datetime.now().isoformat(),
                "intensity": 0.0,
                "angular_intensity": 0.0
            }
        }
        await self.send_message(message)
        response = await self.receive_message()
        return response
    
    async def test_direction_invalid_command(self):
        """测试无效方向命令"""
        logger.info("\n=== 测试 6: 无效方向命令 ===")
        message = {
            "type": "direction_result",
            "data": {
                "command": "invalid_command",
                "timestamp": datetime.now().isoformat()
            }
        }
        await self.send_message(message)
        response = await self.receive_message()
        return response
    
    async def test_direction_missing_command(self):
        """测试缺少命令字段"""
        logger.info("\n=== 测试 7: 缺少命令字段 ===")
        message = {
            "type": "direction_result",
            "data": {
                "timestamp": datetime.now().isoformat(),
                "intensity": 0.5
            }
        }
        await self.send_message(message)
        response = await self.receive_message()
        return response
    
    # ========== AngleMessageHandler 测试 ==========
    
    async def test_angle_positive(self):
        """测试正角度值"""
        logger.info("\n=== 测试 8: 正角度值 (45°) ===")
        message = {
            "type": "angle_value",
            "data": {
                "angle": 45.0,
                "timestamp": datetime.now().isoformat()
            }
        }
        await self.send_message(message)
        response = await self.receive_message()
        return response
    
    async def test_angle_negative(self):
        """测试负角度值"""
        logger.info("\n=== 测试 9: 负角度值 (-90°) ===")
        message = {
            "type": "angle_value",
            "data": {
                "angle": -90.0,
                "timestamp": datetime.now().isoformat()
            }
        }
        await self.send_message(message)
        response = await self.receive_message()
        return response
    
    async def test_angle_zero(self):
        """测试零角度"""
        logger.info("\n=== 测试 10: 零角度 ===")
        message = {
            "type": "angle_value",
            "data": {
                "angle": 0.0,
                "timestamp": datetime.now().isoformat()
            }
        }
        await self.send_message(message)
        response = await self.receive_message()
        return response
    
    async def test_angle_max(self):
        """测试最大角度值"""
        logger.info("\n=== 测试 11: 最大角度值 (360°) ===")
        message = {
            "type": "angle_value",
            "data": {
                "angle": 360.0,
                "timestamp": datetime.now().isoformat()
            }
        }
        await self.send_message(message)
        response = await self.receive_message()
        return response
    
    async def test_angle_out_of_range(self):
        """测试超出范围的角度"""
        logger.info("\n=== 测试 12: 超出范围角度 (400°) ===")
        message = {
            "type": "angle_value",
            "data": {
                "angle": 400.0,
                "timestamp": datetime.now().isoformat()
            }
        }
        await self.send_message(message)
        response = await self.receive_message()
        return response
    
    async def test_angle_missing_field(self):
        """测试缺少角度字段"""
        logger.info("\n=== 测试 13: 缺少角度字段 ===")
        message = {
            "type": "angle_value",
            "data": {
                "timestamp": datetime.now().isoformat()
            }
        }
        await self.send_message(message)
        response = await self.receive_message()
        return response
    
    async def test_angle_invalid_type(self):
        """测试无效角度类型"""
        logger.info("\n=== 测试 14: 无效角度类型 ===")
        message = {
            "type": "angle_value",
            "data": {
                "angle": "not_a_number",
                "timestamp": datetime.now().isoformat()
            }
        }
        await self.send_message(message)
        response = await self.receive_message()
        return response
    
    # ========== 混合测试 ==========
    
    async def test_rapid_messages(self):
        """测试快速连续发送消息"""
        logger.info("\n=== 测试 15: 快速连续消息 ===")
        
        messages = [
            {
                "type": "direction_result",
                "data": {
                    "command": "forward",
                    "timestamp": datetime.now().isoformat(),
                    "intensity": 0.8
                }
            },
            {
                "type": "angle_value",
                "data": {
                    "angle": 30.0,
                    "timestamp": datetime.now().isoformat()
                }
            },
            {
                "type": "direction_result",
                "data": {
                    "command": "turn_left",
                    "timestamp": datetime.now().isoformat(),
                    "intensity": 0.6
                }
            }
        ]
        
        for msg in messages:
            await self.send_message(msg)
            await asyncio.sleep(0.1)  # 短暂延迟
            response = await self.receive_message(timeout=1.0)
        
        return True


async def run_all_tests():
    """运行所有测试"""
    tester = BrokerHandlerTester()
    
    # 连接
    if not await tester.connect():
        logger.error("无法连接到服务器，测试终止")
        return
    
    try:
        # DirectionMessageHandler 测试
        logger.info("\n" + "="*60)
        logger.info("开始测试 DirectionMessageHandler")
        logger.info("="*60)
        
        await tester.test_direction_forward()
        await asyncio.sleep(0.5)
        
        await tester.test_direction_turn_left()
        await asyncio.sleep(0.5)
        
        await tester.test_direction_turn_right()
        await asyncio.sleep(0.5)
        
        await tester.test_direction_backward()
        await asyncio.sleep(0.5)
        
        await tester.test_direction_stationary()
        await asyncio.sleep(0.5)
        
        await tester.test_direction_invalid_command()
        await asyncio.sleep(0.5)
        
        await tester.test_direction_missing_command()
        await asyncio.sleep(0.5)
        
        # AngleMessageHandler 测试
        logger.info("\n" + "="*60)
        logger.info("开始测试 AngleMessageHandler")
        logger.info("="*60)
        
        await tester.test_angle_positive()
        await asyncio.sleep(0.5)
        
        await tester.test_angle_negative()
        await asyncio.sleep(0.5)
        
        await tester.test_angle_zero()
        await asyncio.sleep(0.5)
        
        await tester.test_angle_max()
        await asyncio.sleep(0.5)
        
        await tester.test_angle_out_of_range()
        await asyncio.sleep(0.5)
        
        await tester.test_angle_missing_field()
        await asyncio.sleep(0.5)
        
        await tester.test_angle_invalid_type()
        await asyncio.sleep(0.5)
        
        # 混合测试
        logger.info("\n" + "="*60)
        logger.info("开始混合测试")
        logger.info("="*60)
        
        await tester.test_rapid_messages()
        
        logger.info("\n" + "="*60)
        logger.info("所有测试完成！")
        logger.info("="*60)
        
    except Exception as e:
        logger.error(f"测试过程中出错: {e}")
    finally:
        await tester.close()


async def run_interactive_mode():
    """交互模式 - 手动发送消息"""
    tester = BrokerHandlerTester()
    
    if not await tester.connect():
        logger.error("无法连接到服务器")
        return
    
    logger.info("\n进入交互模式，输入 'quit' 退出")
    logger.info("示例消息格式:")
    logger.info('  方向: {"type":"direction_result","data":{"command":"forward","timestamp":"2024-01-01T00:00:00","intensity":0.8}}')
    logger.info('  角度: {"type":"angle_value","data":{"angle":45.0,"timestamp":"2024-01-01T00:00:00"}}')
    
    try:
        while True:
            user_input = input("\n输入消息 (JSON): ").strip()
            
            if user_input.lower() == 'quit':
                break
            
            if not user_input:
                continue
            
            try:
                message = json.loads(user_input)
                await tester.send_message(message)
                response = await tester.receive_message()
            except json.JSONDecodeError:
                logger.error("无效的 JSON 格式")
            except Exception as e:
                logger.error(f"错误: {e}")
    
    finally:
        await tester.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        asyncio.run(run_interactive_mode())
    else:
        asyncio.run(run_all_tests())
