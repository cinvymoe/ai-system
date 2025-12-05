# 数据迁移指南

本指南说明如何使用数据迁移脚本管理摄像头数据库。

## 功能概述

数据迁移脚本 (`src/migrate_data.py`) 提供以下功能：

1. **导入示例数据** - 导入预定义的示例摄像头数据
2. **导出数据** - 将当前数据库数据导出为 JSON 文件
3. **导入数据** - 从 JSON 文件导入摄像头数据
4. **清空数据** - 清空数据库中的所有摄像头数据
5. **查看统计** - 显示数据库统计信息

## 使用方法

### 前置条件

确保已安装 Python 依赖：

```bash
cd backend
uv pip install -e .
```

### 1. 导入示例数据

首次使用时，可以导入预定义的示例摄像头数据：

```bash
python src/migrate_data.py --import-sample
```

这将导入 6 个示例摄像头，包括：
- 前方主摄像头
- 前方辅助摄像头
- 后方摄像头
- 左侧摄像头
- 右侧摄像头
- 备用摄像头

### 2. 导出数据

将当前数据库中的所有摄像头数据导出到 JSON 文件：

```bash
python src/migrate_data.py --export cameras_backup.json
```

导出的 JSON 文件格式：

```json
[
  {
    "id": "camera-forward-1",
    "name": "前方主摄像头",
    "url": "rtsp://192.168.1.101:554/stream1",
    "enabled": true,
    "resolution": "1920x1080",
    "fps": 30,
    "brightness": 50,
    "contrast": 50,
    "status": "online",
    "direction": "forward",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
]
```

### 3. 导入数据

从 JSON 文件导入摄像头数据：

```bash
# 导入新数据（跳过已存在的摄像头）
python src/migrate_data.py --import cameras_backup.json

# 导入并替换已存在的摄像头
python src/migrate_data.py --import cameras_backup.json --replace
```

**注意：**
- 默认情况下，如果摄像头 ID 已存在，将跳过该摄像头
- 使用 `--replace` 选项可以更新已存在的摄像头

### 4. 清空数据

清空数据库中的所有摄像头数据：

```bash
python src/migrate_data.py --clear
```

**警告：** 此操作会删除所有数据，执行前会要求确认。

### 5. 查看统计信息

显示数据库统计信息：

```bash
python src/migrate_data.py --stats
```

输出示例：

```
Database Statistics
============================================================

Total cameras: 6
Enabled cameras: 4
Online cameras: 3

Cameras by direction:
  forward: 2
  backward: 1
  left: 1
  right: 1
  idle: 1
```

## 常见使用场景

### 场景 1：首次设置

```bash
# 1. 初始化数据库并导入示例数据
python src/migrate_data.py --import-sample

# 2. 查看导入结果
python src/migrate_data.py --stats
```

### 场景 2：数据备份

```bash
# 定期备份数据
python src/migrate_data.py --export backups/cameras_$(date +%Y%m%d).json
```

### 场景 3：数据恢复

```bash
# 从备份恢复数据
python src/migrate_data.py --import backups/cameras_20240101.json --replace
```

### 场景 4：环境迁移

```bash
# 在开发环境导出数据
python src/migrate_data.py --export dev_cameras.json

# 在生产环境导入数据
python src/migrate_data.py --import dev_cameras.json
```

### 场景 5：重置数据库

```bash
# 清空现有数据
python src/migrate_data.py --clear

# 重新导入示例数据
python src/migrate_data.py --import-sample
```

## JSON 文件格式

导入的 JSON 文件必须是一个摄像头对象数组，每个对象包含以下字段：

### 必填字段

- `id` (string): 摄像头唯一标识符
- `name` (string): 摄像头名称
- `url` (string): RTSP 流地址
- `direction` (string): 方向 ('forward', 'backward', 'left', 'right', 'idle')

### 可选字段

- `enabled` (boolean): 是否启用，默认 true
- `resolution` (string): 分辨率，默认 "1920x1080"
- `fps` (integer): 帧率，默认 30
- `brightness` (integer): 亮度 (0-100)，默认 50
- `contrast` (integer): 对比度 (0-100)，默认 50
- `status` (string): 状态 ('online', 'offline')，默认 'offline'

### 自动生成字段

以下字段会自动生成，导入时会被忽略：
- `created_at`: 创建时间
- `updated_at`: 更新时间

## 错误处理

脚本会处理以下错误情况：

1. **文件不存在** - 导入时如果文件不存在会显示错误
2. **JSON 格式错误** - 无效的 JSON 格式会显示错误
3. **数据验证失败** - 不符合数据模型的数据会被跳过
4. **重复 ID** - 默认跳过，使用 `--replace` 可以更新
5. **数据库错误** - 数据库操作失败会回滚并显示错误

## 最佳实践

1. **定期备份** - 在进行重大更改前先导出数据
2. **版本控制** - 将导出的 JSON 文件纳入版本控制
3. **测试导入** - 在测试环境先验证导入操作
4. **保留备份** - 保留多个时间点的备份文件
5. **文档记录** - 记录每次迁移操作的目的和结果

## 故障排除

### 问题：导入失败

**可能原因：**
- JSON 格式错误
- 数据验证失败
- 数据库连接问题

**解决方法：**
1. 检查 JSON 文件格式是否正确
2. 验证数据字段是否符合要求
3. 确认数据库文件权限正确

### 问题：导出为空

**可能原因：**
- 数据库中没有数据
- 数据库连接失败

**解决方法：**
1. 使用 `--stats` 检查数据库状态
2. 确认数据库文件存在
3. 检查数据库初始化是否成功

### 问题：权限错误

**可能原因：**
- 脚本没有执行权限
- 数据库文件权限不足

**解决方法：**
```bash
# 添加执行权限
chmod +x src/migrate_data.py

# 检查数据库文件权限
ls -l data/vision_security.db
```

## 技术细节

### 数据库模型

摄像头数据模型定义在 `src/models/camera.py`：

```python
class Camera(Base):
    __tablename__ = "cameras"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    url = Column(String, nullable=False)
    enabled = Column(Boolean, default=True)
    resolution = Column(String, default="1920x1080")
    fps = Column(Integer, default=30)
    brightness = Column(Integer, default=50)
    contrast = Column(Integer, default=50)
    status = Column(String, default="offline")
    direction = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### 示例数据

示例数据定义在脚本的 `SAMPLE_CAMERAS` 常量中，可以根据需要修改。

### 扩展功能

如需添加自定义迁移逻辑，可以修改脚本中的以下函数：
- `import_sample_data()` - 修改示例数据
- `export_data()` - 自定义导出格式
- `import_data()` - 添加数据转换逻辑

## 相关文档

- [数据库设计文档](../.kiro/specs/camera-database-integration/design.md)
- [需求文档](../.kiro/specs/camera-database-integration/requirements.md)
- [API 文档](src/api/cameras.py)

## 支持

如有问题或建议，请查看项目文档或联系开发团队。
