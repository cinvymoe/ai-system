#!/usr/bin/env python3
"""
快速测试 WebSocket 连接
"""

import asyncio
import json
import websockets
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_websocket():
    uri = "ws://localhost:8000/api/sensor/stream"
    
    try:
        async with websockets.connect(uri) as websocket:
            logger.info("WebSocket 连接成功")
            
            # 等待并接收前几条消息
            for i in range(5):
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    data = json.loads(message)
                    
                    msg_type = data.get('type', 'unknown')
                    logger.info(f"[{i+1}] 收到消息类型: {msg_type}")
                    
                    if msg_type == 'sensor_data':
                        sensor_info = data.get('data', {})
                        acc = sensor_info.get('acceleration', {})
                        logger.info(f"    加速度: X={acc.get('x', 0):.3f}g")
                    
                    elif msg_type == 'error':
                        error_info = data.get('data', {})
                        logger.error(f"    错误: {error_info.get('error', 'Unknown')}")
                        if 'available_fields' in error_info:
                            logger.info(f"    可用字段: {error_info['available_fields']}")
                    
                except asyncio.TimeoutError:
                    logger.warning(f"等待消息 {i+1} 超时")
                    break
                except json.JSONDecodeError as e:
                    logger.error(f"JSON 解析错误: {e}")
                    logger.error(f"原始消息: {message}")
            
            logger.info("测试完成")
    
    except Exception as e:
        logger.error(f"WebSocket 测试失败: {e}")

if __name__ == '__main__':
    asyncio.run(test_websocket())