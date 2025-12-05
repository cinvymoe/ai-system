# Vision Security Backend

Python 后端服务，用于视觉安全监控系统。

## 技术栈

- **Python**: >=3.10
- **FastAPI**: Web 框架
- **uvicorn**: ASGI 服务器
- **uv**: 包管理工具

## 项目结构

```
backend/
├── src/                    # 源代码
│   ├── __init__.py
│   └── main.py            # 应用入口
├── tests/                 # 测试
│   └── __init__.py
├── .venv/                 # 虚拟环境（由 uv 创建）
├── pyproject.toml         # 项目配置
└── README.md              # 本文件
```

## 开发环境设置

### 前置要求

- Python 3.10 或更高版本
- uv 包管理工具

### 安装 uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 初始化项目

1. 创建虚拟环境：

```bash
cd backend
uv venv
```

2. 激活虚拟环境：

```bash
# Linux/macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

3. 安装依赖（使用国内镜像）：

```bash
uv pip install -i https://pypi.tuna.tsinghua.edu.cn/simple fastapi uvicorn
```

或者直接使用 uv sync（如果配置了镜像）：

```bash
uv sync
```

### 安装开发依赖

```bash
uv pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -e ".[dev]"
```

## 运行应用

### 开发模式

使用 uvicorn 运行（带自动重载）：

```bash
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

或者直接运行 main.py：

```bash
uv run python src/main.py
```

### 访问应用

- API 文档（Swagger UI）: http://localhost:8000/docs
- API 文档（ReDoc）: http://localhost:8000/redoc
- 健康检查: http://localhost:8000/health
- 根路径: http://localhost:8000/

## API 端点

### 基础端点

#### GET /

返回欢迎消息。

**响应示例：**
```json
{
  "message": "Hello World",
  "service": "Vision Security Backend"
}
```

#### GET /health

健康检查端点。

**响应示例：**
```json
{
  "status": "healthy"
}
```

### 摄像头管理端点

#### GET /api/cameras

获取所有摄像头列表。

#### GET /api/cameras/{camera_id}

获取指定摄像头详情。

#### POST /api/cameras

创建新摄像头。

#### PATCH /api/cameras/{camera_id}

更新摄像头信息。

#### DELETE /api/cameras/{camera_id}

删除摄像头。

### 摄像头在线检查端点 🆕

#### POST /api/cameras/{camera_id}/check-status

检查指定摄像头是否在线，并自动更新状态。

**响应示例：**
```json
{
  "camera_id": "cam-001",
  "camera_name": "前方摄像头",
  "url": "rtsp://192.168.1.100:554/stream",
  "previous_status": "offline",
  "current_status": "online",
  "is_online": true,
  "status_changed": true
}
```

#### POST /api/cameras/check-all-status

检查所有摄像头是否在线，并自动更新状态。

**响应示例：**
```json
{
  "total_cameras": 4,
  "online_count": 3,
  "offline_count": 1,
  "status_changed_count": 2,
  "cameras": [...]
}
```

**使用示例：**

```bash
# 检查单个摄像头
curl -X POST "http://localhost:8000/api/cameras/cam-001/check-status"

# 检查所有摄像头
curl -X POST "http://localhost:8000/api/cameras/check-all-status"
```

详细使用说明请参考 [examples/camera_online_check_example.md](examples/camera_online_check_example.md)。

### 摄像头自动监控 🆕

后端服务启动后会自动开启定时监控，每 5 分钟检查一次所有摄像头的在线状态。

#### GET /api/cameras/monitor/status

查看监控服务状态。

**响应示例：**
```json
{
  "is_running": true,
  "check_interval_minutes": 5,
  "last_check_time": "2024-12-02T10:30:00",
  "total_checks": 3,
  "next_check_time": "2024-12-02T10:35:00"
}
```

**配置选项：**

通过环境变量配置监控行为：

```bash
# 检查间隔（分钟）
export CAMERA_CHECK_INTERVAL_MINUTES=5

# 连接超时（秒）
export CAMERA_CHECK_TIMEOUT_SECONDS=5

# 启用/禁用自动监控
export ENABLE_AUTO_MONITORING=true
```

详细配置和使用指南请参考 [CAMERA_MONITOR_GUIDE.md](CAMERA_MONITOR_GUIDE.md)。

## 测试

运行测试：

```bash
uv run pytest
```

运行测试并显示覆盖率：

```bash
uv run pytest --cov=src tests/
```

## 代码格式化

使用 black 格式化代码：

```bash
uv run black src/ tests/
```

使用 ruff 进行代码检查：

```bash
uv run ruff check src/ tests/
```

## 配置国内镜像

如果需要永久配置 uv 使用国内镜像，可以设置环境变量：

```bash
# Linux/macOS
export UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple

# Windows
set UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
```

或者在 `pyproject.toml` 中添加：

```toml
[[tool.uv.index]]
url = "https://pypi.tuna.tsinghua.edu.cn/simple"
```

## 数据库管理

### 初始化数据库

首次运行时，数据库会自动初始化。也可以手动初始化：

```bash
python src/init_database.py
```

### 数据迁移

详细的数据迁移指南请参考 [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)。

#### 快速开始

导入示例数据：

```bash
python src/migrate_data.py --import-sample
```

或使用快速设置脚本：

```bash
./scripts/setup_initial_data.sh
```

#### 常用命令

```bash
# 查看数据库统计
python src/migrate_data.py --stats

# 导出数据备份
python src/migrate_data.py --export backups/cameras.json

# 从备份恢复数据
python src/migrate_data.py --import backups/cameras.json --replace

# 自动备份（使用脚本）
./scripts/backup_data.sh
```

## 未来扩展

- ✅ API 路由模块（api/）
- ✅ 核心业务逻辑（services/）
- ✅ 数据模型（models/）
- ✅ 数据库集成（SQLite + SQLAlchemy）
- 认证和授权
- WebSocket 支持

## 许可证

待定
