#!/usr/bin/env python3
"""
调试 collect_stream 方法
"""

import asyncio
import logging
from src.collectors.sensors.jy901 import JY901Sensor

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def debug_collect_stream():
    """调试 collect_stream 方法"""
    logger.info("开始调试 collect_stream...")
    
    sensor = JY901Sensor(
        sensor_id="debug_test",
        config={
            'mode': 'realtime',
            'port': '/dev/ttyACM0',
            'baudrate': 9600,
            'timeout': 1.0,
        }
    )
    
    try:
        # 连接传感器
        logger.info("连接传感器...")
        if not await sensor.connect():
            logger.error("传感器连接失败")
            return
        
        logger.info("传感器连接成功")
        
        # 测试 collect_stream
        logger.info("开始测试 collect_stream...")
        
        count = 0
        timeout_count = 0
        
        try:
            async for collected_data in sensor.collect_stream():
                count += 1
                logger.info(f"[{count}] 收到数据")
                
                # 检查数据
                sensor_data = collected_data.metadata.get('data', {})
                logger.info(f"    数据字段数量: {len(sensor_data)}")
                
                if sensor_data:
                    logger.info(f"    字段: {list(sensor_data.keys())[:5]}...")  # 只显示前5个字段
                    
                    # 显示一些关键数据
                    if '加速度X(g)' in sensor_data:
                        acc_x = sensor_data['加速度X(g)']
                        logger.info(f"    加速度X: {acc_x}")
                else:
                    logger.warning("    数据为空")
                
                # 限制测试次数
                if count >= 3:
                    logger.info("收到足够数据，停止测试")
                    break
                
                # 超时检查
                timeout_count += 1
                if timeout_count > 100:  # 10秒超时
                    logger.warning("测试超时")
                    break
                    
        except asyncio.TimeoutError:
            logger.error("collect_stream 超时")
        except Exception as e:
            logger.error(f"collect_stream 错误: {e}", exc_info=True)
        
        await sensor.disconnect()
        logger.info("传感器已断开")
        
    except Exception as e:
        logger.error(f"调试失败: {e}", exc_info=True)

if __name__ == '__main__':
    asyncio.run(debug_collect_stream())