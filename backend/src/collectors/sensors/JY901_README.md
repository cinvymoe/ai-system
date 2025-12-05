# JY901 九轴传感器采集器

JY901/JY901S 是一款高性能的九轴姿态传感器，集成了三轴加速度计、三轴陀螺仪和三轴磁力计。

## 功能特性

### 支持的数据类型

- **加速度** (X, Y, Z) - 单位: g
- **角速度** (X, Y, Z) - 单位: °/s
- **角度** (X, Y, Z) - 单位: °
- **磁场** (X, Y, Z) - 单位: uT
- **四元数** (Q0, Q1, Q2, Q3)
- **温度** - 单位: °C
- **电量** - 单位: %

### 工作模式

1. **回放模式 (playback)** - 从本地数据文件读取数据
2. **实时模式 (realtime)** - 从串口实时读取数据（待实现）

## 快速开始

### 1. 基础使用

```python
import asyncio
from collectors.sensors import JY901Sensor

async def main():
    # 创建传感器实例
    sensor = JY901Sensor(
        sensor_id='jy901_001',
        data_file_path='datahandler/data/20250529101647.txt',
        config={
            'mode': 'playback',      # 回放模式
            'interval': 0.01,        # 数据间隔 10ms
            'loop': False            # 不循环播放
        }
    )
    
    # 连接传感器
    await sensor.connect()
    
    # 采集数据
    async for data in sensor.collect():
        # 获取加速度数据
        acc = sensor.get_acceleration()
        print(f"加速度: X={acc['x']:.3f}g, Y={acc['y']:.3f}g, Z={acc['z']:.3f}g")
        
        # 获取角速度数据
        gyro = sensor.get_gyroscope()
        print(f"角速度: X={gyro['x']:.2f}°/s, Y={gyro['y']:.2f}°/s, Z={gyro['z']:.2f}°/s")
        
        # 获取温度和电量
        temp = sensor.get_temperature()
        battery = sensor.get_battery()
        print(f"温度: {temp:.1f}°C, 电量: {battery:.0f}%")
        
        break  # 只采集一条数据
    
    # 清理资源
    await sensor.cleanup()

asyncio.run(main())
```

### 2. 循环播放模式

```python
sensor = JY901Sensor(
    sensor_id='jy901_002',
    data_file_path='datahandler/data/20250529101647.txt',
    config={
        'mode': 'playback',
        'interval': 0.01,
        'loop': True  # 启用循环播放
    }
)

await sensor.connect()

# 数据会循环播放，直到手动停止
count = 0
async for data in sensor.collect():
    count += 1
    # 处理数据...
    
    if count >= 1000:  # 采集1000条后停止
        break

await sensor.cleanup()
```

### 3. 获取所有传感器数据

```python
await sensor.connect()

async for data in sensor.collect():
    # 加速度
    acc = sensor.get_acceleration()
    # {'x': 0.005, 'y': -0.006, 'z': 1.029}
    
    # 角速度
    gyro = sensor.get_gyroscope()
    # {'x': -2.014, 'y': -0.244, 'z': 0.0}
    
    # 角度
    angle = sensor.get_angle()
    # {'x': 0.14, 'y': 0.81, 'z': -1.27}
    
    # 磁场
    mag = sensor.get_magnetic()
    # {'x': -7.533, 'y': -31.727, 'z': -65.107}
    
    # 四元数
    quat = sensor.get_quaternion()
    # {'q0': 0.99988, 'q1': -0.00317, 'q2': 0.00443, 'q3': -0.01105}
    
    # 温度
    temp = sensor.get_temperature()
    # 30.6
    
    # 电量
    battery = sensor.get_battery()
    # 0
    
    break

await sensor.cleanup()
```

### 4. 监控播放进度

```python
await sensor.connect()

async for data in sensor.collect():
    progress = sensor.get_progress()
    print(f"进度: {progress['current_index']}/{progress['total_count']} "
          f"({progress['progress']:.1f}%)")
    
    # 处理数据...

await sensor.cleanup()
```

## 数据文件格式

JY901 传感器使用制表符分隔的文本文件格式：

```
时间	设备名称	片上时间()	加速度X(g)	加速度Y(g)	加速度Z(g)	角速度X(°/s)	角速度Y(°/s)	角速度Z(°/s)	角度X(°)	角度Y(°)	角度Z(°)	磁场X(uT)	磁场Y(uT)	磁场Z(uT)	四元数0()	四元数1()	四元数2()	四元数3()	温度(°C)	版本号()	电量(%)
2025-5-29 10:16:47.928	/dev/bus/usb/001/002	2025-5-29 10:13:4:428	0.005	-0.006	1.029	-2.014	-0.244	0.000	0.14	0.81	-1.27	-7.533	-31.727	-65.107	0.99988	-0.00317	0.00443	-0.01105	30.6	33291	0
```

### 数据有效性验证

采集器会自动验证数据的有效性，包括：

- 加速度范围: -16g ~ 16g
- 角速度范围: -2000°/s ~ 2000°/s
- 角度范围: -180° ~ 180°
- 温度范围: -40°C ~ 85°C
- 电量范围: 0% ~ 100%

无效数据会被自动过滤。

## 配置参数

### 初始化参数

```python
JY901Sensor(
    sensor_id: str,              # 传感器唯一标识
    data_file_path: str = None,  # 数据文件路径（回放模式必需）
    config: dict = None          # 配置参数
)
```

### 配置选项

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| mode | str | 'playback' | 工作模式: 'playback' 或 'realtime' |
| interval | float | 0.01 | 数据发送间隔（秒） |
| loop | bool | False | 是否循环播放数据 |

## API 参考

### 连接和断开

```python
await sensor.connect()      # 连接传感器
await sensor.disconnect()   # 断开连接
await sensor.cleanup()      # 清理资源（推荐使用）
```

### 数据采集

```python
async for data in sensor.collect():
    # data 是 CollectedData 对象
    # data.status - 采集状态
    # data.data - 原始数据字典
    # data.metadata - 元数据
    # data.timestamp - 时间戳
    pass
```

### 数据读取

```python
# 读取原始数据
data = await sensor.read_sensor_data()

# 获取加速度
acc = sensor.get_acceleration()
# 返回: {'x': float, 'y': float, 'z': float}

# 获取角速度
gyro = sensor.get_gyroscope()
# 返回: {'x': float, 'y': float, 'z': float}

# 获取角度
angle = sensor.get_angle()
# 返回: {'x': float, 'y': float, 'z': float}

# 获取磁场
mag = sensor.get_magnetic()
# 返回: {'x': float, 'y': float, 'z': float}

# 获取四元数
quat = sensor.get_quaternion()
# 返回: {'q0': float, 'q1': float, 'q2': float, 'q3': float}

# 获取温度
temp = sensor.get_temperature()
# 返回: float

# 获取电量
battery = sensor.get_battery()
# 返回: float

# 获取播放进度
progress = sensor.get_progress()
# 返回: {'current_index': int, 'total_count': int, 'progress': float}
```

## 运行示例

项目提供了多个使用示例：

```bash
cd backend
python -m src.collectors.sensors.examples
```

示例包括：
1. 基础使用
2. 连续采集
3. 数据分析
4. 循环播放模式
5. 完整传感器数据

## 集成到现有系统

JY901Sensor 实现了 `IDataSource` 接口，可以无缝集成到现有的数据采集框架中：

```python
from collectors.sensors import JY901Sensor
from collectors.interfaces import IProcessor, IStorageBackend

# 创建传感器
sensor = JY901Sensor(
    sensor_id='jy901_001',
    data_file_path='data/sensor_data.txt'
)

# 创建处理器和存储后端
processor = MyProcessor()
storage = MyStorageBackend()

# 数据采集流程
await sensor.connect()

async for collected_data in sensor.collect():
    # 处理数据
    processed = await processor.process(collected_data)
    
    # 存储数据
    await storage.store(processed)

await sensor.cleanup()
```

## 注意事项

1. **资源管理**: 使用完毕后务必调用 `cleanup()` 方法释放资源
2. **线程安全**: 内部使用线程锁保证数据访问的线程安全
3. **数据验证**: 自动验证数据有效性，无效数据会被过滤
4. **实时模式**: 目前仅支持回放模式，实时串口模式待实现

## 故障排除

### 问题: 连接失败

```python
# 检查数据文件路径是否正确
sensor = JY901Sensor(
    sensor_id='jy901_001',
    data_file_path='正确的文件路径.txt'
)
```

### 问题: 数据为空

```python
# 确保数据文件格式正确，包含表头和数据行
# 检查数据是否通过有效性验证
```

### 问题: 内存占用过高

```python
# 使用较大的 interval 值减少数据采集频率
sensor = JY901Sensor(
    sensor_id='jy901_001',
    data_file_path='data.txt',
    config={'interval': 0.1}  # 100ms 间隔
)
```

## 相关文档

- [传感器采集器基类文档](README.md)
- [数据采集接口文档](../API_DOCUMENTATION.md)
- [集成指南](../INTEGRATION_GUIDE.md)
