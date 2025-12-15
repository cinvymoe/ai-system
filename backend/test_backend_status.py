#!/usr/bin/env python3
"""
测试后端服务状态
"""

import asyncio
import aiohttp
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_backend_status():
    """测试后端服务状态"""
    try:
        async with aiohttp.ClientSession() as session:
            # 测试根路径
            async with session.get('http://localhost:8000/') as response:
                logger.info(f"根路径状态: {response.status}")
                
            # 测试 API 文档
            async with session.get('http://localhost:8000/docs') as response:
                logger.info(f"API 文档状态: {response.status}")
                
        logger.info("后端服务正在运行")
        return True
        
    except aiohttp.ClientConnectorError:
        logger.error("无法连接到后端服务 (localhost:8000)")
        return False
    except Exception as e:
        logger.error(f"测试后端状态失败: {e}")
        return False

if __name__ == '__main__':
    asyncio.run(test_backend_status())