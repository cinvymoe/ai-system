# 传感器采集模块

该模块提供各种传感器的数据采集功能。

## 目录结构

```
sensors/
├── __init__.py          # 模块初始化
├── base.py              # 传感器采集器基类
├── README.md            # 本文档
└── examples/            # 示例实现（待添加）
```

## 快速开始

### 1. 创建自定义传感器采集器

继承 `BaseSensorCollector` 类并实现必要的方法：

```python
from collectors.sensors import BaseSensorCollector
from typing import Dict, Any

class TemperatureSensor(BaseSensorCollector):
    """温度传感器采集器"""
    
    async def connect(self) -> bool:
        """连接到温度传感器"""
        # 实现连接逻辑
        self._is_connected = True
        return True
    
    async def disconnect(self) -> None:
        """断开连接"""
        self._is_connected = False
    
    async def read_sensor_data(self) -> Dict[str, Any]:
        """读取温度数据"""
        # 实现数据读取逻辑
        return {
            'temperature': 25.5,
            'unit': 'celsius',
            'humidity': 60.0
        }
```

### 2. 使用传感器采集器

```python
import asyncio

async def main():
    # 创建传感器实例
    sensor = TemperatureSensor(
        sensor_id='temp_001',
        sensor_type='temperature',
        config={'port': '/dev/ttyUSB0'}
    )
    
    # 采集数据
    async for data in sensor.collect():
        print(f"采集状态: {data.status}")
        print(f"传感器数据: {data.data}")
        print(f"元数据: {data.metadata}")
    
    # 清理资源
    await sensor.cleanup()

asyncio.run(main())
```

## 基类说明

### BaseSensorCollector

传感器采集器基类，提供以下功能：

#### 初始化参数

- `sensor_id`: 传感器唯一标识
- `sensor_type`: 传感器类型（如 'temperature', 'humidity', 'pressure' 等）
- `config`: 传感器配置参数（可选）

#### 必须实现的方法

- `connect()`: 连接到传感器
- `disconnect()`: 断开传感器连接
- `read_sensor_data()`: 读取传感器原始数据

#### 已实现的方法

- `collect()`: 采集数据并返回 CollectedData 对象
- `validate()`: 验证传感器连接和配置
- `cleanup()`: 清理资源

## 扩展开发

### 添加新的传感器类型

1. 在 `sensors/` 目录下创建新的传感器模块文件
2. 继承 `BaseSensorCollector` 类
3. 实现必要的抽象方法
4. 在 `__init__.py` 中导出新的传感器类

### 示例：添加湿度传感器

```python
# sensors/humidity.py
from .base import BaseSensorCollector
from typing import Dict, Any

class HumiditySensor(BaseSensorCollector):
    """湿度传感器采集器"""
    
    async def connect(self) -> bool:
        # 实现连接逻辑
        pass
    
    async def disconnect(self) -> None:
        # 实现断开逻辑
        pass
    
    async def read_sensor_data(self) -> Dict[str, Any]:
        # 实现数据读取逻辑
        pass
```

然后在 `__init__.py` 中添加：

```python
from .humidity import HumiditySensor

__all__ = [
    'BaseSensorCollector',
    'HumiditySensor',
]
```

## 注意事项

1. 所有传感器采集器都应该继承 `BaseSensorCollector`
2. 确保在使用完毕后调用 `cleanup()` 方法释放资源
3. 异常处理已在基类中实现，会自动返回失败状态的 CollectedData
4. 传感器数据应该包含时间戳和必要的元数据

## 相关文档

- [数据采集接口文档](../API_DOCUMENTATION.md)
- [集成指南](../INTEGRATION_GUIDE.md)
- [快速开始](../QUICK_START.md)
