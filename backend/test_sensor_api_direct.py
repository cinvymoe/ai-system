#!/usr/bin/env python3
"""
直接测试传感器 API 逻辑
"""

import asyncio
import logging
from src.collectors.sensors.jy901 import JY901Sensor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_sensor_api_logic():
    """测试传感器 API 的逻辑"""
    logger.info("测试传感器 API 逻辑...")
    
    # 创建传感器实例（模拟 API 中的逻辑）
    sensor_device = JY901Sensor(
        sensor_id="jy901_sensor_ws",
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
        if not await sensor_device.connect():
            logger.error("传感器连接失败")
            return
        
        logger.info("传感器连接成功")
        
        # 启动数据采集
        if not sensor_device.is_running:
            sensor_device.is_running = True
        
        # 等待传感器初始化
        logger.info("等待传感器数据准备...")
        await asyncio.sleep(2)
        
        # 测试数据流
        logger.info("开始测试数据流...")
        count = 0
        
        async for collected_data in sensor_device.collect_stream():
            count += 1
            logger.info(f"[{count}] 收到数据")
            
            # 检查数据
            sensor_data = collected_data.metadata.get('data', {})
            logger.info(f"    数据字段: {list(sensor_data.keys())}")
            
            if sensor_data:
                # 检查必需字段
                required_fields = ['加速度X(g)', '加速度Y(g)', '加速度Z(g)']
                missing_fields = [field for field in required_fields if field not in sensor_data]
                
                if missing_fields:
                    logger.warning(f"    缺少字段: {missing_fields}")
                else:
                    logger.info("    ✓ 所有必需字段都存在")
                    
                    # 显示一些数据
                    acc_x = sensor_data.get('加速度X(g)', 0)
                    acc_y = sensor_data.get('加速度Y(g)', 0)
                    acc_z = sensor_data.get('加速度Z(g)', 0)
                    temp = sensor_data.get('温度(°C)', 0)
                    
                    logger.info(f"    加速度: ({acc_x:.3f}, {acc_y:.3f}, {acc_z:.3f})g")
                    logger.info(f"    温度: {temp:.1f}°C")
            else:
                logger.warning("    数据为空")
            
            if count >= 3:
                logger.info("测试完成，收到足够的数据")
                break
        
        await sensor_device.disconnect()
        logger.info("传感器已断开")
        
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)

if __name__ == '__main__':
    asyncio.run(test_sensor_api_logic())