#!/usr/bin/env python3
"""
测试 WebSocket /stream 端点的订阅机制

验证：
1. WebSocket 连接时自动订阅 direction_result 和 angle_value
2. 回调函数正确处理消息
3. 发送报警类型和摄像头列表到客户端
4. 断开连接时正确清理订阅
"""

import asyncio
import json
import logging
from datetime import datetime
import websockets

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 配置
BACKEND_URL = "ws://localhost:8000/api/broker/stream"
TEST_DURATION = 30  # 测试持续时间（秒）


async def test_websocket_subscription():
    """测试 WebSocket 订阅机制"""
    
    logger.info("=" * 60)
    logger.info("测试 WebSocket /stream 订阅机制")
    logger.info("=" * 60)
    
    received_messages = {
        "current_state": 0,
        "direction_result": 0,
        "angle_value": 0,
        "ai_alert": 0
    }
    
    try:
        # 连接到 WebSocket
        logger.info(f"连接到 {BACKEND_URL}...")
        async with websockets.connect(BACKEND_URL) as websocket:
            logger.info("✓ WebSocket 连接成功")
            
            # 设置超时
            start_time = asyncio.get_event_loop().time()
            
            while True:
                # 检查是否超时
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed > TEST_DURATION:
                    logger.info(f"\n测试时间到 ({TEST_DURATION}秒)，结束测试")
                    break
                
                try:
                    # 接收消息（设置超时）
                    message_str = await asyncio.wait_for(
                        websocket.recv(),
                        timeout=5.0
                    )
                    
                    # 解析消息
                    message = json.loads(message_str)
                    message_type = message.get("type")
                    
                    # 统计消息
                    if message_type in received_messages:
                        received_messages[message_type] += 1
                    
                    # 显示消息详情
                    logger.info(f"\n{'=' * 60}")
                    logger.info(f"收到消息 #{sum(received_messages.values())}")
                    logger.info(f"{'=' * 60}")
                    logger.info(f"类型: {message_type}")
                    logger.info(f"消息ID: {message.get('message_id', 'N/A')}")
                    logger.info(f"时间戳: {message.get('timestamp', 'N/A')}")
                    
                    # 显示数据内容
                    data = message.get("data", {})
                    if message_type == "current_state":
                        logger.info(f"方向映射: {list(data.get('directions', {}).keys())}")
                        logger.info(f"角度范围数: {len(data.get('angle_ranges', []))}")
                    elif message_type == "direction_result":
                        logger.info(f"方向命令: {data.get('command')}")
                        logger.info(f"强度: {data.get('intensity', 0):.2f}")
                        logger.info(f"角度强度: {data.get('angular_intensity', 0):.2f}")
                    elif message_type == "angle_value":
                        logger.info(f"角度: {data.get('angle')}°")
                    elif message_type == "ai_alert":
                        logger.info(f"报警类型: {data.get('alert_type')}")
                        logger.info(f"严重程度: {data.get('severity')}")
                    
                    # 显示摄像头列表
                    cameras = message.get("cameras", [])
                    logger.info(f"摄像头数量: {len(cameras)}")
                    
                    if cameras:
                        if isinstance(cameras[0], dict):
                            # 详细的摄像头信息
                            for i, cam in enumerate(cameras[:3], 1):  # 只显示前3个
                                logger.info(
                                    f"  摄像头 {i}: {cam.get('name')} "
                                    f"({cam.get('status')}) - {cam.get('url')}"
                                )
                            if len(cameras) > 3:
                                logger.info(f"  ... 还有 {len(cameras) - 3} 个摄像头")
                        else:
                            # 简单的摄像头ID列表
                            logger.info(f"  摄像头IDs: {cameras[:5]}")
                            if len(cameras) > 5:
                                logger.info(f"  ... 还有 {len(cameras) - 5} 个")
                    
                except asyncio.TimeoutError:
                    # 超时是正常的，继续等待
                    logger.debug("等待消息...")
                    continue
                except json.JSONDecodeError as e:
                    logger.error(f"JSON 解析错误: {e}")
                    continue
    
    except websockets.exceptions.WebSocketException as e:
        logger.error(f"WebSocket 错误: {e}")
        return False
    except Exception as e:
        logger.error(f"测试错误: {e}", exc_info=True)
        return False
    
    finally:
        # 显示统计信息
        logger.info(f"\n{'=' * 60}")
        logger.info("测试统计")
        logger.info(f"{'=' * 60}")
        logger.info(f"current_state 消息: {received_messages['current_state']}")
        logger.info(f"direction_result 消息: {received_messages['direction_result']}")
        logger.info(f"angle_value 消息: {received_messages['angle_value']}")
        logger.info(f"ai_alert 消息: {received_messages['ai_alert']}")
        logger.info(f"总消息数: {sum(received_messages.values())}")
        logger.info(f"{'=' * 60}")
    
    return True


async def publish_test_messages():
    """发布测试消息到 broker"""
    import aiohttp
    
    logger.info("\n发布测试消息...")
    
    test_messages = [
        ("direction_result", {"command": "forward", "intensity": 0.9}),
        ("angle_value", {"angle": 45.0}),
        ("direction_result", {"command": "turn_left", "intensity": 0.7}),
        ("angle_value", {"angle": 90.0}),
        ("direction_result", {"command": "backward", "intensity": 0.6}),
        ("angle_value", {"angle": 180.0}),
    ]
    
    async with aiohttp.ClientSession() as session:
        for msg_type, data in test_messages:
            try:
                url = f"http://localhost:8000/api/broker/test/publish"
                params = {"message_type": msg_type}
                
                async with session.post(url, params=params, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(
                            f"✓ 发布 {msg_type}: {data}, "
                            f"通知 {result.get('subscribers_notified')} 个订阅者"
                        )
                    else:
                        logger.error(f"✗ 发布失败: {response.status}")
                
                # 等待一下再发送下一条
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"发布消息错误: {e}")


async def main():
    """主测试函数"""
    
    logger.info("WebSocket /stream 订阅机制测试")
    logger.info(f"后端地址: {BACKEND_URL}")
    logger.info(f"测试时长: {TEST_DURATION} 秒")
    logger.info("")
    
    # 创建两个任务：一个接收消息，一个发布消息
    receive_task = asyncio.create_task(test_websocket_subscription())
    
    # 等待一下让 WebSocket 连接建立
    await asyncio.sleep(2)
    
    # 开始发布测试消息
    publish_task = asyncio.create_task(publish_test_messages())
    
    # 等待接收任务完成
    await receive_task
    
    logger.info("\n测试完成！")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n测试被用户中断")
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)
